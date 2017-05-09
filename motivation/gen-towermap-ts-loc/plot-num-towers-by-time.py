#!/usr/bin/env python

import datetime
import os
import sys

sys.path.insert(0, "%s/work/mutant/ec2-tools/lib/util" % os.path.expanduser("~"))
import Cons
import Util

import Conf
import Plot
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
	fn_towersbuilt_by_tsrange = TowerData.GetNumTowersBuiltByTsRange()
	Cons.P(fn_towersbuilt_by_tsrange)


if __name__ == "__main__":
	sys.exit(main(sys.argv))
