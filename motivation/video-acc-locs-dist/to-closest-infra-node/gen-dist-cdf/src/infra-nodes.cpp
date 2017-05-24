#include <fstream>
#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>
#include <boost/geometry/index/rtree.hpp>


#include "conf.h"
#include "cons.h"
#include "infra-nodes.h"
#include "usa-map.h"
#include "util.h"

using namespace std;

namespace InfraNodes {

void _BuildCtLocIndex();
void _BuildApLocIndex();

namespace bg = boost::geometry;
namespace bgi = boost::geometry::index;
typedef bg::model::point<double, 2, bg::cs::cartesian> point;

vector<point> _ct_locs;
vector<point> _ap_locs;
vector<point> _cdn_locs;

typedef std::pair<point, int> _value;
bgi::rtree<_value, bgi::quadratic<16> > _rtree_ct;
bgi::rtree<_value, bgi::quadratic<16> > _rtree_ap;
bgi::rtree<_value, bgi::quadratic<16> > _rtree_cdn;

bool _dev = false;

void _LoadCT() {
	Cons::MT _("Loading CT locations ...");

	const string fn = Conf::GetFn("ct_loc");
	ifstream ifs(fn);
	if (! ifs.is_open())
		THROW(boost::format("Unable to open file %s") % fn);

	static const auto sep = boost::is_any_of(" ");
	string line;
	int i = 0;
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
		if (_dev) {
			i ++;
			if (i == 1000)
				break;
		}
	}
	Cons::P(boost::format("Loaded %d points") % _ct_locs.size());
}


void _LoadAP() {
	Cons::MT _("Loading AP locations ...");

	const string fn = Conf::GetFn("ap_loc");
	ifstream ifs(fn);
	if (! ifs.is_open())
		THROW(boost::format("Unable to open file %s") % fn);

	static const auto sep = boost::is_any_of(" ");
	string line;
	int i = 0;
	while (getline(ifs, line)) {
		if (line.size() == 0)
			continue;
		if (line[0] == '#')
			continue;
		//Cons::P(line);
		vector<string> t;
		boost::split(t, line, sep, boost::token_compress_on);
		if (t.size() != 2)
			THROW("Unexpected");
		// 39.7861 -75.6907
		float lat = atof(t[0].c_str());
		float lon = atof(t[1].c_str());
		_ap_locs.push_back(point(lon, lat));
		if (_dev) {
			i ++;
			if (i == 1000)
				break;
		}
	}
	Cons::P(boost::format("Loaded %d points") % _ap_locs.size());
}


void _LoadCdn() {
	Cons::MT _("Loading CDN locations ...");

	const string fn = Conf::GetFn("cdn_loc");
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
		//Cons::P(line);
		vector<string> t;
		boost::split(t, line, sep, boost::token_compress_on);
		if (t.size() != 5)
			THROW("Unexpected");
		// abe    isp      US  -75.440806 40.652083
		float lat = atof(t[3].c_str());
		float lon = atof(t[4].c_str());
		_cdn_locs.push_back(point(lon, lat));
	}
	Cons::P(boost::format("Loaded %d points") % _cdn_locs.size());
}


void _BuildCtLocIndex() {
	Cons::MT _("Building CT location index ...");

	int i = 0;
	for (const auto& l: _ct_locs) {
		_rtree_ct.insert(std::make_pair(l, i));
		i ++;
		if (i % 1000 == 0) {
			Cons::ClearLine();
			Cons::Pnnl(boost::format("%d (%.2f%%)") % i % (100.0 * i / _ct_locs.size()));
		}
	}
	Cons::ClearLine();
	Cons::P(boost::format("%d (%.2f%%)") % i % (100.0 * i / _ct_locs.size()));
}


void _BuildApLocIndex() {
	Cons::MT _("Building AP location index ...");

	int i = 0;
	for (const auto& l: _ap_locs) {
		_rtree_ap.insert(std::make_pair(l, i));
		i ++;
		if (i % 1000 == 0) {
			Cons::ClearLine();
			Cons::Pnnl(boost::format("%d (%.2f%%)") % i % (100.0 * i / _ap_locs.size()));
		}
	}
	Cons::ClearLine();
	Cons::P(boost::format("%d (%.2f%%)") % i % (100.0 * i / _ap_locs.size()));
}


void _BuildCdnLocIndex() {
	Cons::MT _("Building CDN location index ...");

	int i = 0;
	for (const auto& l: _cdn_locs) {
		_rtree_cdn.insert(std::make_pair(l, i));
		i ++;
		if (i % 1000 == 0) {
			Cons::ClearLine();
			Cons::Pnnl(boost::format("%d (%.2f%%)") % i % (100.0 * i / _cdn_locs.size()));
		}
	}
	Cons::ClearLine();
	Cons::P(boost::format("%d (%.2f%%)") % i % (100.0 * i / _cdn_locs.size()));
}


void Load() {
	_LoadCT();
	_LoadAP();
	_LoadCdn();
	_BuildCtLocIndex();
	_BuildApLocIndex();
	_BuildCdnLocIndex();
}


//void GetDistFromRandPntToClosestNode() {
//	_BuildCtLocIndex();
//
//	UsaMap::Load();
//
//	for (int i = 0; i < 10; i ++) {
//		CPoint p = UsaMap::GenRandPntInUsa();
//		//Cons::P(boost::format("%f %f") % p.x % p.y);
//
//		vector<_value> result_n;
//		point p1(p.x, p.y);
//		_rtree_ct.query(bgi::nearest(p1, 1), std::back_inserter(result_n));
//		if (result_n.size() != 1)
//			THROW("Unexpected");
//		const point& np = result_n[0].first;
//		//int np_idx = result_n[0].second;
//		double np_x = bg::get<0>(np);
//		double np_y = bg::get<1>(np);
//		double d = Util::ArcInMeters(p.x, p.y, np_x, np_y);
//		Cons::P(d);
//	}
//}


double DistToClosest(const NodeType nt, const point& p) {
	vector<_value> result_n;
	if (nt == NodeType::CT) {
		_rtree_ct.query(bgi::nearest(p, 1), std::back_inserter(result_n));
	} else if (nt == NodeType::AP) {
		_rtree_ap.query(bgi::nearest(p, 1), std::back_inserter(result_n));
	} else if (nt == NodeType::CDN) {
		_rtree_cdn.query(bgi::nearest(p, 1), std::back_inserter(result_n));
	}

	if (result_n.size() != 1)
		THROW("Unexpected");
	const point& np = result_n[0].first;

	double x = bg::get<0>(p);
	double y = bg::get<1>(p);
	double np_x = bg::get<0>(np);
	double np_y = bg::get<1>(np);
	return Util::ArcInMeters(x, y, np_x, np_y);
}
};
