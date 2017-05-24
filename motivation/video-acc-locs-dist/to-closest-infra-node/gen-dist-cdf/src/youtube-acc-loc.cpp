#include <boost/filesystem.hpp>
#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point.hpp>

#include "conf.h"
#include "infra-nodes.h"
#include "stat.h"
#include "youtube-acc-loc.h"

using namespace std;

namespace YoutubeAccLoc {

namespace bg = boost::geometry;
typedef bg::model::point<double, 2, bg::cs::cartesian> point;
vector<point> _video_acc_locs;

void Load() {
	Cons::MT _("Loading YouTube access locations ...");

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
		_video_acc_locs.push_back(point(lon, lat));
	}
	Cons::P(boost::format("Loaded %d locations") % _video_acc_locs.size());
}


void CalcDistsToInfraNodes() {
	Cons::MT _("Calc dist to closest infra nodes ...");

	// Distance to the nearest infra nodes
	vector<double> dists_to_ct;
	vector<double> dists_to_ap;
	vector<double> dists_to_cdn;
	for (const auto& p: _video_acc_locs) {
		dists_to_ct.push_back(InfraNodes::DistToClosest(InfraNodes::NodeType::CT, p));
		dists_to_ap.push_back(InfraNodes::DistToClosest(InfraNodes::NodeType::AP, p));
		dists_to_cdn.push_back(InfraNodes::DistToClosest(InfraNodes::NodeType::CDN, p));
	}

	const string dn = Conf::GetFn("out_dn");
	boost::filesystem::create_directories(dn);
	Stat::Gen<double>(dists_to_ct,  str(boost::format("%s/video-acc-dist-to-closest-ct-cdf") % dn));
	Stat::Gen<double>(dists_to_ap,  str(boost::format("%s/video-acc-dist-to-closest-ap-cdf") % dn));
	Stat::Gen<double>(dists_to_cdn, str(boost::format("%s/video-acc-dist-to-closest-cdn-cdf") % dn));
}

};
