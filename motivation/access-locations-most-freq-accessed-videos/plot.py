#!/usr/bin/env python

import os
import re
import sys

sys.path.insert(0, "%s/work/mec-node-placement/etc" % os.path.expanduser("~"))
import Cons
import Util


def main(argv):
	dn_in = "%s/gen-data/.result/acc-locs" % os.path.dirname(__file__)
	GenInFiles(dn_in)

	dn_out = "%s/.result" % os.path.dirname(__file__)
	Util.MkDirs(dn_out)

	fn_out = "%s/youtube-video-acc-locs.pdf" % dn_out

	with Cons.MT("Plotting YouTube video access locations ..."):
		env = os.environ.copy()
		env["IN_FNS"] = " ".join(_in_fns)
		env["IN_DN"] = dn_in
		env["OUT_FN"] = fn_out
		Util.RunSubp("gnuplot %s/loc.gnuplot" % os.path.dirname(__file__), env=env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


_in_fns = []

def GenInFiles(dn):
	global _in_fns

	ranks = []
	for fn in os.listdir(dn):
		#Cons.P(fn)
		mo = re.match(r"(?P<rank>\d\d\d)-(\d|\w|-){11}", fn)
		if mo is not None:
			ranks.append(int(mo.group("rank")))
			_in_fns.append(fn)
		else:
			Cons.P(fn)

	ranks.sort()
	_in_fns.sort()

	all_exists = True
	if len(ranks) != 100:
		all_exists = False

	if all_exists:
		for i in range(1, 100+1):
			if ranks[i - 1] != i:
				Cons.P("file starting with %d doesn't exist" % i)
				all_exists = False
				break
	
	if all_exists:
		return

	raise RuntimeError("Implement calling the data generator")


if __name__ == "__main__":
	sys.exit(main(sys.argv))
