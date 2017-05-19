#include <fstream>
#include <mutex>
#include <thread>

#include <boost/algorithm/string.hpp>
#include <boost/format.hpp>
#include <boost/filesystem.hpp>

#include "conf.h"
#include "cons.h"
#include "op-youtube.h"
#include "stat.h"
#include "util.h"
#include "youtube-data.h"

using namespace std;

namespace YoutubeData {
	// youtube
	vector<Op*> _entries;

	const vector<Op*>& Entries() {
		return _entries;
	}

	void _LoadOps() {
		string fn = Conf::GetFn("in_file");
		string dn = boost::filesystem::path(fn).parent_path().string();
		string fn1 = boost::filesystem::path(fn).filename().string();

		// Unzip if a zipped file exist
		if (! boost::filesystem::exists(fn)) {
			string fn_7z = fn + ".7z";
			if (boost::filesystem::exists(fn_7z)) {
				string cmd = str(boost::format("cd %s && 7z e %s.7z") % dn % fn1);
				Util::RunSubprocess(cmd);
			} else
				THROW("Unexpected");
		}

		Cons::MT _(boost::format("Loading YouTube workload from file %s ...") % fn);

		ifstream ifs(fn.c_str(), ios::binary);
		if (! ifs.is_open())
			THROW(boost::format("unable to open file %1%") % fn);

		size_t e_size;
		ifs.read((char*)&e_size, sizeof(e_size));

		long num_in_usa = 0;
		long num_outside_usa = 0;
		for (size_t i = 0; i < e_size; i ++) {
			Op* e = new OpYoutube(ifs);
			_entries.push_back(e);

			// Assume all operations are reads
			//if (e->type == Op::Type::W)
			//	_num_writes ++;
			//else if (e->type == Op::Type::R)
			//	_num_reads ++;

			if (e->in_usa == 'Y')
				num_in_usa ++;
			else
				num_outside_usa ++;

			if (i % 10000 == 0) {
				Cons::ClearLine();
				Cons::Pnnl(boost::format("%.2f%%") % (100.0 * i / e_size));
			}
		}
		Cons::ClearLine();
		Cons::P("100.00%");

		// 80% of YouTube's views are from outside of the U.S. [https://fortunelords.com/youtube-statistics]
		Cons::P(boost::format("loaded %d ops. in_usa=%d (%.2f%%). outside_usa=%d (%.2f%%)")
				% _entries.size()
				% num_in_usa
				% (100.0 * num_in_usa / _entries.size())
				% num_outside_usa
				% (100.0 * num_outside_usa / _entries.size())
				);
	}

	void _SetCreatedAtPt0(int start, int end) {
		//Cons::P(boost::format("%d %d") % start % end);
		for (int i = start; i < end; i ++) {
			Op* op = _entries[i];
			op->SetCreatedAtPt();
		}
	}

	void _SetCreatedAtPt() {
		Cons::MT _("Setting created_at_pt ...");
		bool parallel = true;

		if (parallel) {
			int num_cpus = std::thread::hardware_concurrency();
			int s = _entries.size();
			int num_items = int(ceil(float(s) / num_cpus));

			vector<thread*> threads;
			for (int i = 0; i < num_cpus; i ++) {
				int start = i * num_items;
				int end = std::min((i + 1) * num_items, s);

				thread* t = new thread(_SetCreatedAtPt0, start, end);
				threads.push_back(t);
			}

			for (auto t: threads) {
				t->join();
				delete t;
			}
		} else {
			for (Op* op: _entries)
				op->SetCreatedAtPt();
		}
	}


	void Load() {
		_LoadOps();
		//_SetCreatedAtPt();
	}

	void GenNumAccessesByVideos() {
		Cons::MT _("Gen num accesses stat by videos ...");

		map<string, int> vid_cnt;
		for (const Op* op: _entries) {
			const string& vid = op->obj_id;

			auto it = vid_cnt.find(vid);
			if (it == vid_cnt.end()) {
				vid_cnt[vid] = 1;
			} else {
				(it->second) ++;
			}
		}

		vector<int> cnts;
		for (auto it: vid_cnt)
			cnts.push_back(it.second);
		sort(cnts.begin(), cnts.end());

		const string fn = Conf::GetFn("out_file");
		ofstream ofs(fn);
		if (! ofs.is_open())
			THROW(boost::format("unable to open file %1%") % fn);
		string fmt = "%6d %4d";
		ofs << Util::BuildHeader(fmt, "video_rank num_accesses") << "\n";
		int i = 0;
		int prev_c = -1;
		int c = 0;
		for (auto it = cnts.rbegin(); it != cnts.rend(); ++ it) {
			i ++;
			c = *it;
			if (prev_c != c) {
				ofs << boost::format(fmt + "\n") % i % c;
				prev_c = c;
			}
		}
		ofs << boost::format(fmt + "\n") % i % c;
		ofs.close();
		Cons::P(boost::format("Created %s %d") % fn % boost::filesystem::file_size(fn));
	}

#if 0
	void GenNumAccessesByVideos() {
		Cons::MT _("Gen num accesses stat by videos ...");

		map<string, int> vid_cnt;
		for (const Op* op: _entries) {
			const string& vid = op->obj_id;

			auto it = vid_cnt.find(vid);
			if (it == vid_cnt.end()) {
				vid_cnt[vid] = 1;
			} else {
				(it->second) ++;
			}
		}

		struct VidCnt {
			string vid;
			int cnt;

			VidCnt(const string& vid_, const int cnt_)
				: vid(vid_), cnt(cnt_)
			{}

			bool operator < (const VidCnt& r) const {
				if (cnt < r.cnt) return true;
				if (cnt > r.cnt) return false;

				return vid < r.vid;
			}
		};

		vector<VidCnt> vec_vid_cnt;
		for (auto it: vid_cnt)
			vec_vid_cnt.push_back(VidCnt(it.first, it.second));
		sort(vec_vid_cnt.begin(), vec_vid_cnt.end());

		const string fn = Conf::GetFn("out_file");
		ofstream ofs(fn);
		if (! ofs.is_open())
			THROW(boost::format("unable to open file %1%") % fn);
		for (auto it = vec_vid_cnt.rbegin(); it != vec_vid_cnt.rend(); ++ it)
			ofs << boost::format("%s %4d\n") % it->vid % it->cnt;
		ofs.close();
		Cons::P(boost::format("Created %s %d") % fn % boost::filesystem::file_size(fn));
	}
#endif

	void GenNumAccessesByVideosCdf() {
		Cons::MT _("Gen num accesses stat by videos CDF ...");

		map<string, int> vid_cnt;
		for (const Op* op: _entries) {
			const string& vid = op->obj_id;

			auto it = vid_cnt.find(vid);
			if (it == vid_cnt.end()) {
				vid_cnt[vid] = 1;
			} else {
				(it->second) ++;
			}
		}

		vector<int> cnts;
		for (auto it: vid_cnt)
			cnts.push_back(it.second);
		sort(cnts.begin(), cnts.end());

		Stat::Gen<int>(cnts, Conf::GetFn("out_file"));

		//const string fn = Conf::GetFn("out_file");
		//ofstream ofs(fn);
		//if (! ofs.is_open())
		//	THROW(boost::format("unable to open file %1%") % fn);
		//for (auto it = cnts.rbegin(); it != cnts.rend(); ++ it)
		//	ofs << boost::format("%s %4d\n") % it->vid % it->cnt;
		//ofs.close();
		//Cons::P(boost::format("Created %s %d") % fn % boost::filesystem::file_size(fn));
	}

	void FreeMem() {
		if (_entries.size() == 0)
			return;

		Cons::MT _("Freeing ops ...");
		for (auto e: _entries)
			delete e;
	}
}
