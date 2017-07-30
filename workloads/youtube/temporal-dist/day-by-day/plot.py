#!/usr/bin/env python

import os
import sys

sys.path.insert(0, "%s/work/cp-mec/etc" % os.path.expanduser("~"))
import Cons
import Util

#_fn_in = "%s/work/cp-mec-data/170703-095232-tweets-97822" % os.path.expanduser("~")
_fn_in = "%s/work/cp-mec-data/170729-104532-tweets-983810" % os.path.expanduser("~")

_dist_sq_threshold = 0.02
_dn_plot_data = "%s/.output" % os.path.dirname(__file__)


def main(argv):
  Util.MkDirs(_dn_plot_data)
  Plot()


def Plot():
  fn_in = GetTemporalDist()
  fn_out = "%s.pdf" % fn_in

  with Cons.MT("Plotting temporal distribution ..."):
    env = os.environ.copy()
    env["FN_IN"] = fn_in
    env["FN_OUT"] = fn_out
    Util.RunSubp("gnuplot %s/temporal-dist.gnuplot" % os.path.dirname(__file__), env=env)
    Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def GetTemporalDist():
  fn_out = "%s/%s-temporal-dist" % (_dn_plot_data, os.path.basename(_fn_in))
  if os.path.isfile(fn_out):
    return fn_out
  cmd = "%s/gen-plot-data.sh --youtube_workload=%s" % (os.path.dirname(__file__), _fn_in)
  Util.RunSubp(cmd)
  return fn_out


if __name__ == "__main__":
  sys.exit(main(sys.argv))
