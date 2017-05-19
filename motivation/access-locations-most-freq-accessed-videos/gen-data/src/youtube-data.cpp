#include <fstream>
#include <mutex>
#include <thread>

#include <boost/algorithm/string.hpp>
#include <boost/format.hpp>
#include <boost/filesystem.hpp>

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

	void GenAccLocsByVidoes() {
		Cons::MT _("Gen access locations by videos ...");

		struct Coord {
			double lon;
			double lat;
			Coord(double lon_, double lat_)
				: lon(lon_), lat(lat_)
			{}
		};

		// map<video_id, ...
		map<string, vector<Coord> > vid_locs;

		for (const Op* op: _entries) {
			const string& vid = op->obj_id;
			auto it = vid_locs.find(vid);
			if (it == vid_locs.end())
				vid_locs[vid] = vector<Coord>();
			vid_locs[vid].push_back(Coord(op->lon, op->lat));
		}

		// Sort the videos by the number of accesses
		vector<string> vids;
		for (auto it: vid_locs)
			vids.push_back(it.first);
		sort(vids.begin(), vids.end(), 
				[&vid_locs](const string& a, const string& b) -> bool { 
					return vid_locs[a].size() < vid_locs[b].size();
				}
			);

		// Check top vids. Strange: chZmtjD8rxw has 1157 Tweets and only 5140 views.
		// That's the only one out of the top 10 videos.
		if (false) {
			int i = 0;
			for (auto it = vids.rbegin(); it != vids.rend(); ++ it) {
				const string& vid = *it;
				Cons::P(boost::format("%s %d") % vid % vid_locs[vid].size());
				i ++;
				if (i == 10)
					break;
			}
		}

		// Save access locations of the top 100 videos
		const string dn = Conf::GetFn("out_dn");
		boost::filesystem::create_directories(dn);
		int num_files = 100;

		int i = 0;
		for (auto it = vids.rbegin(); it != vids.rend(); ++ it) {
			i ++;
			const string& vid = *it;
			const string fn = str(boost::format("%s/%03d-%s") % dn % i % vid);
			ofstream ofs(fn);
			if (! ofs.is_open())
				THROW(boost::format("unable to open file %1%") % fn);
			ofs << boost::format("# video_id: %s\n") % vid;
			for (auto l: vid_locs[vid])
				ofs << boost::format("%f %f\n") % l.lon % l.lat;
			if (i == num_files)
				break;
		}

		Cons::P(boost::format("Created %d files in %s") % num_files % dn);
	}


	void FreeMem() {
		if (_entries.size() == 0)
			return;

		Cons::MT _("Freeing ops ...");
		for (auto e: _entries)
			delete e;
	}
}
