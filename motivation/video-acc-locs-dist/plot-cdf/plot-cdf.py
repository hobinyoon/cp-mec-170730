#!/usr/bin/env python

import os
import sys

sys.path.insert(0, "%s/work/mutant/ec2-tools/lib/util" % os.path.expanduser("~"))
import Cons
import Util


_dn_result = "%s/.result" % os.path.dirname(__file__)


def main(argv):
	Util.MkDirs(_dn_result)

	dn = "%s/work/mec-node-placement/motivation/video-acc-locs-dist" % os.path.expanduser("~")

	# Distance CDF to clustering centers, nearest CTs, APs, and CDNs.
	fn_cc = "%s/to-clustering-center/.result/001-Y4MnpzG5Sqc-dist-to-clustering-center-cdf" % dn
	dn1 = "%s/to-closest-infra-node/gen-dist-cdf/.result" % dn
	fn_ct = "%s/video-acc-dist-to-closest-ct-cdf" % dn1
	fn_ap = "%s/video-acc-dist-to-closest-ap-cdf" % dn1
	fn_cdn = "%s/video-acc-dist-to-closest-cdn-cdf" % dn1
	fn_out = "%s/video-to-infra-node-dist.pdf" % _dn_result

	with Cons.MT("Plotting clustered locations ..."):
		env = os.environ.copy()
		env["FN_CC"] = fn_cc
		env["FN_CT"] = fn_ct
		env["FN_AP"] = fn_ap
		env["FN_CDN"] = fn_cdn
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/dist-cdf.gnuplot" % os.path.dirname(__file__), env=env, measure_time=True)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


if __name__ == "__main__":
	sys.exit(main(sys.argv))
