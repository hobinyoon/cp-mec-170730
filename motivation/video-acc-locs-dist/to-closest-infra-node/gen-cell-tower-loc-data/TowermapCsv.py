import os
import sys

sys.path.insert(0, "%s/work/mutant/ec2-tools/lib/util" % os.path.expanduser("~"))
import Cons
import Util

import Conf

def GetFile():
	fn_in = "%s/work/castnet-data/towermap-dec-2016/pgdb_FCC_ASR_December_2016.mdb" % os.path.expanduser("~")
	fn_out = "%s/pgdb_FCC_ASR_December_2016.CO_EB_latlong_Height.csv" % Conf.dn_result

	if os.path.isfile(fn_out):
		return fn_out

	with Cons.MT("Generating the csv file ..."):
		cmd = "mdb-export %s CO_EB_latlong_Height > %s" % (fn_in, fn_out)
		Util.RunSubp(cmd, env=os.environ.copy(), measure_time=True)
		return fn_out
