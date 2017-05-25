#!/usr/bin/env python

import os
import pprint
import re
import sys

sys.path.insert(0, "%s/work/mutant/ec2-tools/lib/util" % os.path.expanduser("~"))
import Cons
import Util


_dn_result = "%s/.result" % os.path.dirname(__file__)
_fn_cc = None


def main(argv):
	Util.MkDirs(_dn_result)

	dn = "%s/work/mec-node-placement/motivation/video-acc-locs-dist" % os.path.expanduser("~")

	# Distance CDF to clustering centers, nearest CTs, APs, and CDNs.
	global _fn_cc
	_fn_cc = "%s/to-clustering-center/.result/001-Y4MnpzG5Sqc-dist-to-clustering-center-cdf" % dn
	dn1 = "%s/to-closest-infra-node/gen-dist-cdf/.result" % dn
	fn_ct = "%s/video-acc-dist-to-closest-ct-cdf" % dn1
	fn_ap = "%s/video-acc-dist-to-closest-ap-cdf" % dn1
	fn_cdn = "%s/video-acc-dist-to-closest-cdn-cdf" % dn1
	fn_out = "%s/video-acc-dist-to-clustering-centers-infra-nodes.pdf" % _dn_result

	with Cons.MT("Plotting clustered locations ..."):
		env = os.environ.copy()
		env["FN_CC"] = _fn_cc
		env["FN_CT"] = fn_ct
		env["FN_AP"] = fn_ap
		env["FN_CDN"] = fn_cdn
		env["STAT_CT"]  = _GetStatInStr(fn_ct)
		env["STAT_AP"]  = _GetStatInStr(fn_ap)
		env["STAT_CDN"] = _GetStatInStr(fn_cdn)
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/dist-cdf.gnuplot" % os.path.dirname(__file__), env=env, measure_time=True)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _GetStatInStr(fn):
	stat = {}
	with open(fn) as fo:
		for line in fo:
			if len(line) == 0:
				continue
			if line[0] != "#":
				continue
			#Cons.P(line)
			t = re.split(r" +", line.strip())
			if len(t) != 3:
				raise RuntimeError("Unexpected")
			# avg 1316.29
			k = t[1]
			v = float(t[2])
			stat[k] = v
	#return stat

	# Calc y-coord. -1, if no intersection.
	y = _Y(stat["avg"])

	return " ".join(str(i) for i in [stat["avg"], stat["1p"], stat["99p"], y])


_dist_to_cc_cdf = None
def _Y(x):
	global _dist_to_cc_cdf
	if _dist_to_cc_cdf is None:
		_dist_to_cc_cdf = {}
		with open(_fn_cc) as fo:
			for line in fo:
				if len(line) == 0:
					continue
				if line[0] == "#":
					continue
				t = line.strip().split(" ")
				if len(t) != 2:
					raise RuntimeError("Unexpected")
				dist = float(t[0])
				cdf = float(t[1])
				_dist_to_cc_cdf[dist] = cdf
	d_prev = None
	cdf_prev = None
	for d, cdf in sorted(_dist_to_cc_cdf.iteritems()):
		if d_prev is not None:
			if (d_prev <= x) and (x <= d):
				# y - cdf_prev : cdf - cdf_prev = x - d_prev : d - d_prev
				# y - cdf_prev = (cdf - cdf_prev) * (x - d_prev) / (d - d_prev)
				# y = (cdf - cdf_prev) * (x - d_prev) / (d - d_prev) + cdf_prev
				return (cdf - cdf_prev) * (x - d_prev) / (d - d_prev) + cdf_prev
		d_prev = d
		cdf_prev = cdf
	return -1


if __name__ == "__main__":
	sys.exit(main(sys.argv))
