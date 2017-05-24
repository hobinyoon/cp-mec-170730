#include <fstream>
#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>
#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point.hpp>
#include <boost/geometry/index/rtree.hpp>


#include "conf.h"
#include "cons.h"
#include "infra-nodes.h"
#include "stat.h"
#include "usa-map.h"
#include "util.h"

using namespace std;

namespace InfraNodes {

void _BuildInfraNodeLocIndex();

namespace bg = boost::geometry;
namespace bgi = boost::geometry::index;
typedef bg::model::point<double, 2, bg::cs::cartesian> point;


vector<point> _ct_locs;

void Load() {
	Cons::MT _("Loading CT locations ...");

	const string fn = str(boost::format("%s/../gen-cell-tower-loc-data/.result/towers-ts-coord") % boost::filesystem::path(__FILE__).parent_path().string());

	ifstream ifs(fn);
	if (! ifs.is_open())
		THROW(boost::format("Unable to open file %s") % fn);

	static const auto sep = boost::is_any_of(" ");
	string line;
	while (getline(ifs, line)) {
		//Cons::P(line);
		vector<string> t;
		boost::split(t, line, sep, boost::token_compress_on);
		if (t.size() != 3)
			THROW("Unexpected");
		// 19960723 -85.684444 38.195833
		float lon = atof(t[1].c_str());
		float lat = atof(t[2].c_str());
		_ct_locs.push_back(point(lon, lat));
	}

	Cons::P(boost::format("Loaded %d points") % _ct_locs.size());
}


typedef std::pair<point, int> _value;
bgi::rtree<_value, bgi::quadratic<16> > _rtree;

void GetDistFromRandPntToClosestNode() {
	_BuildInfraNodeLocIndex();

	UsaMap::Load();

	for (int i = 0; i < 10; i ++) {
		CPoint p = UsaMap::GenRandPntInUsa();
		//Cons::P(boost::format("%f %f") % p.x % p.y);

		vector<_value> result_n;
		point p1(p.x, p.y);
		_rtree.query(bgi::nearest(p1, 1), std::back_inserter(result_n));
		if (result_n.size() != 1)
			THROW("Unexpected");
		const point& np = result_n[0].first;
		//int np_idx = result_n[0].second;
		double np_x = bg::get<0>(np);
		double np_y = bg::get<1>(np);
		double d = Util::ArcInMeters(p.x, p.y, np_x, np_y);
		Cons::P(d);
	}
}



void GetDistFromVideoAccessLocToClosestNode() {
	Cons::MT _("Calc dist from video access locations to the nearest infra node ...");

	vector<CPoint> _video_acc_locs;
	{
		const string fn = Conf::GetFn("video_access_loc");
		ifstream ifs(fn);
		if (! ifs.is_open())
			THROW(boost::format("Unable to open file %s") % fn);

		static const auto sep = boost::is_any_of(" ");
		string line;
		while (getline(ifs, line)) {
			if (line.size() == 0)
				continue;
			if (line[0] == '#')
				continue;
			vector<string> t;
			boost::split(t, line, sep, boost::token_compress_on);
			if (t.size() != 2)
				THROW("Unexpected");
			// -96.472461 32.956968
			float lon = atof(t[0].c_str());
			float lat = atof(t[1].c_str());
			_video_acc_locs.push_back(CPoint(lon, lat));
		}
		Cons::P(boost::format("Loaded %d locations") % _video_acc_locs.size());
	}

	_BuildInfraNodeLocIndex();

	vector<double> dists;
	for (const auto& p: _video_acc_locs) {
		vector<_value> result_n;
		point p1(p.x, p.y);
		_rtree.query(bgi::nearest(p1, 1), std::back_inserter(result_n));
		if (result_n.size() != 1)
			THROW("Unexpected");
		const point& np = result_n[0].first;
		//int np_idx = result_n[0].second;
		double np_x = bg::get<0>(np);
		double np_y = bg::get<1>(np);
		double d = Util::ArcInMeters(p.x, p.y, np_x, np_y);
		//Cons::P(d);
		dists.push_back(d);
	}

	const string dn = Conf::GetFn("out_dn");
	boost::filesystem::create_directories(dn);
	Stat::Gen<double>(dists, str(boost::format("%s/video-acc-dist-to-closest-ct-cdf") % dn));
}


void _BuildInfraNodeLocIndex() {
	Cons::MT _("Building location index ...");

	int i = 0;
	for (const auto& l: _ct_locs) {
		_rtree.insert(std::make_pair(l, i));
		i ++;
		if (i % 1000 == 0) {
			Cons::ClearLine();
			Cons::Pnnl(boost::format("%d (%.2f%%)") % i % (100.0 * i / _ct_locs.size()));
		}
		// For dev
		//if (i == 1000)
		//	break;
	}
	Cons::ClearLine();
	Cons::P(boost::format("%d (%.2f%%)") % i % (100.0 * i / _ct_locs.size()));
}

};
