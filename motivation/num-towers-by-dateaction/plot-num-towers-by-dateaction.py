#!/usr/bin/env python

import datetime
import os
import sys

sys.path.insert(0, "%s/work/mutant/ec2-tools/lib/util" % os.path.expanduser("~"))
import Cons
import Util

import Conf
import TowerData


def main(argv):
	# Total 300K towers

	# Extract data (ts and coordinates from the raw towermap file)
	#   Convert to csv
	#   Extract ts and coord

	# Bucketize
	# Plot
	#   Plot by time
	#   Plot locations by time (by year first and see if you need to go in more detail)
	#		  You may or may not want clustering

	Util.MkDirs(Conf.dn_result)

	PlotByTime()
	#PlotLocByTime()


def PlotByTime():
	fn_numtowers_by_timeactions = TowerData.GetNumTowersByTimeActions()
	fn_out = "%s/numtowers-by-timeaction.pdf" % Conf.dn_result

	with Cons.MT("Plotting ..."):
		env = os.environ.copy()
		env["FN_IN"] = fn_numtowers_by_timeactions
		env["FN_OUT"] = fn_out

		Util.RunSubp("gnuplot %s/numtowers-by-timeaction.gnuplot" % os.path.dirname(__file__), env=env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


if __name__ == "__main__":
	sys.exit(main(sys.argv))
