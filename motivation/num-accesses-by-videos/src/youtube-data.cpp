#include <fstream>

#include <boost/algorithm/string.hpp>
#include <boost/format.hpp>
#include <boost/filesystem.hpp>
#include <boost/regex.hpp>

#include "conf.h"
#include "cons.h"
#include "op-youtube.h"
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
		string fn = Conf::GetDir("in_file");
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

	void Load() {
		_LoadOps();
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

		int i = 0;
		for (auto it = vec_vid_cnt.rbegin(); it != vec_vid_cnt.rend(); ++ it) {
			Cons::P(boost::format("%s %4d") % it->vid % it->cnt);

			i ++;
			if (i == 10)
				break;
		}
	}

	void FreeMem() {
		if (_entries.size() == 0)
			return;

		Cons::MT _("Freeing ops ...");
		for (auto e: _entries)
			delete e;
	}
}
