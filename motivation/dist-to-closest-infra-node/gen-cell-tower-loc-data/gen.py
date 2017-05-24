#!/usr/bin/env python

import os
import sys

sys.path.insert(0, "%s/work/mutant/ec2-tools/lib/util" % os.path.expanduser("~"))
import Cons
import Util

import Conf
import TowerData


def main(argv):
	Util.MkDirs(Conf.dn_result)
	fn = TowerData.GetTsCoord()
	Cons.P("Cell tower location file: %s" % fn)


if __name__ == "__main__":
	sys.exit(main(sys.argv))
