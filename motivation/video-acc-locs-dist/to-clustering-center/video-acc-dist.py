#!/usr/bin/env python

import math
import os
import re
import sys

sys.path.insert(0, "%s/work/mutant/ec2-tools/lib/util" % os.path.expanduser("~"))
import Cons
import Util

import Stat

_fn_in0 = "001-Y4MnpzG5Sqc"

_dn_result = "%s/.result" % os.path.dirname(__file__)


def main(argv):
	Util.MkDirs(_dn_result)

	fn_in = GetDistCdfFile()
	fn_out = "%s.pdf" % fn_in

	with Cons.MT("Plotting clustered locations ..."):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/dist-cdf.gnuplot" % os.path.dirname(__file__), env=env, measure_time=True)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def GetDistCdfFile():
	fn_dist_cdf = "%s/%s-dist-cdf" % (_dn_result, _fn_in0)
	if os.path.exists(fn_dist_cdf):
		return fn_dist_cdf

	fn_pnts = "%s/../../cluster-and-plot-video-acc-locs/.result/%s-clustered" % (os.path.dirname(__file__), _fn_in0)
	fn_pnts_c = "%s/../../cluster-and-plot-video-acc-locs/.result/%s-clustered-centers" % (os.path.dirname(__file__), _fn_in0)

	if (not os.path.exists(fn_pnts)) or (not os.path.exists(fn_pnts_c)):
		raise RuntimeError("Implement calling the other script")

	with Cons.MT("Generating dist stat ..."):
		# {cluster_id: [point]}
		cid_pnts = {}
		with Cons.MT("Loading %s ..." % fn_pnts):
			with open(fn_pnts) as fo:
				for line in fo:
					if len(line) == 0:
						continue
					if line[0] == "#":
						continue
					t = re.split(r" +", line.strip())
					if len(t) != 3:
						raise RuntimeError("Unexpected [%s]" % line)
					lon = float(t[0])
					lat = float(t[1])
					# cluster id
					cid = int(t[2])
					if cid not in cid_pnts:
						cid_pnts[cid] = []
					cid_pnts[cid].append((lon, lat))

		# {cluster_id: center}
		cid_c = {}
		with Cons.MT("Loading %s ..." % fn_pnts_c):
			with open(fn_pnts_c) as fo:
				for line in fo:
					if len(line) == 0:
						continue
					if line[0] == "#":
						continue
					t = re.split(r" +", line.strip())
					if len(t) != 4:
						raise RuntimeError("Unexpected [%s]" % line)
					lon = float(t[0])
					lat = float(t[1])
					cid = int(t[3])
					if cid not in cid_c:
						cid_c[cid] = (lon, lat)

		dist = []
		for cid, pnts in cid_pnts.iteritems():
			for p in pnts:
				c = cid_c[cid]
				dist.append(ArcInMeters(c[0], c[1], p[0], p[1]))
		Stat.GenStat(dist, fn_dist_cdf)
		return fn_dist_cdf


# http://en.wikipedia.org/wiki/Haversine_formula
# http://blog.julien.cayzac.name/2008/10/arc-and-distance-between-two-points-on.html
#
#  @brief Computes the arc, in radian, between two WGS-84 positions.
#
# The result is equal to <code>Distance(from,to)/EARTH_RADIUS_IN_METERS</code>
#    <code>= 2*asin(sqrt(h(d/EARTH_RADIUS_IN_METERS )))</code>
#
# where:<ul>
#    <li>d is the distance in meters between 'from' and 'to' positions.</li>
#    <li>h is the haversine function: <code>h(x)=sin^2(x/2)</code></li>
# </ul>
#
# The haversine formula gives:
#    <code>h(d/R) = h(from.lat-to.lat)+h(from.lon-to.lon)+cos(from.lat)*cos(to.lat)</code>
#
# @sa http://en.wikipedia.org/wiki/Law_of_haversines
#
# PI/180
_DEG_TO_RAD = math.pi / 180.0
def ArcInRadians(lon0, lat0, lon1, lat1):
	latitudeArc  = (lat0 - lat1) * _DEG_TO_RAD;
	longitudeArc = (lon0 - lon1) * _DEG_TO_RAD;
	latitudeH = math.sin(latitudeArc * 0.5);
	latitudeH *= latitudeH;
	lontitudeH = math.sin(longitudeArc * 0.5);
	lontitudeH *= lontitudeH;
	tmp = math.cos(lat0 * _DEG_TO_RAD) * math.cos(lat1 * _DEG_TO_RAD);
	return 2.0 * math.asin(math.sqrt(latitudeH + tmp*lontitudeH));

# Earth's quatratic mean radius for WGS-84
_EARTH_RADIUS_IN_METERS = 6372797.560856;
def ArcInMeters(lon0, lat0, lon1, lat1):
	return _EARTH_RADIUS_IN_METERS * ArcInRadians(lon0, lat0, lon1, lat1);


if __name__ == "__main__":
	sys.exit(main(sys.argv))
