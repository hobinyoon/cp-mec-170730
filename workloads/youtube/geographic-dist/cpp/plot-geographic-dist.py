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
  fn_in = GetClusteredPoints()
  max_cluster_size = GetMaxClusterSize(fn_in)
  fn_out = "%s.pdf" % fn_in

  with Cons.MT("Plotting clustered locations ..."):
    env = os.environ.copy()
    env["FN_IN"] = fn_in
    env["MAX_CLUSTER_SIZE"] = str(max_cluster_size)
    env["FN_OUT"] = fn_out
    Util.RunSubp("gnuplot %s/geographic-dist-clustered.gnuplot" % os.path.dirname(__file__), env=env)
    Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def GetClusteredPoints():
  fn_pnts_clustered = "%s/%s-clustered-with-dist-sq-%.3f" % (_dn_plot_data, os.path.basename(_fn_in), _dist_sq_threshold)
  if os.path.isfile(fn_pnts_clustered):
    return fn_pnts_clustered
  cmd = "%s/cluster.sh --youtube_workload=%s --dist_sum_sq_threshold=%f" \
      % (os.path.dirname(__file__), _fn_in, _dist_sq_threshold)
  Util.RunSubp(cmd)
  return fn_pnts_clustered


def GetMaxClusterSize(fn):
  with open(fn) as fo:
    for line in fo:
      line = line.strip()
      if line.startswith("# max_cluster_size="):
        #Cons.P(line)
        t = line.split("=")
        if len(t) != 2:
          raise RuntimeError("Unexpected")
        return int(t[1])
  raise RuntimeError("Unexpected")


if __name__ == "__main__":
  sys.exit(main(sys.argv))
