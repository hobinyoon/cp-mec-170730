#!/usr/bin/env python

import numpy
import os
import pprint
import sys
from rtree import index

sys.path.insert(0, "%s/work/cp-mec/etc" % os.path.expanduser("~"))
import Cons
import Util

#_fn_in = "%s/work/cp-mec-data/170728-103709-tweets-975516" % os.path.expanduser("~")
_fn_in = "%s/work/cp-mec-data/170703-095232-tweets-97822" % os.path.expanduser("~")

_dist_sq_threshold = 0.040
_dn_plot_data = "%s/.output" % os.path.dirname(__file__)
_fn_plot_data = "%s/%s-clustered-with-dist-sq-%.3f" % (_dn_plot_data, os.path.basename(_fn_in), _dist_sq_threshold)


def main(argv):
  Util.MkDirs(_dn_plot_data)

  ClusterPoints()
  Plot()


def ClusterPoints():
  if os.path.isfile(_fn_plot_data):
    return

  points = []
  with Cons.MT("Reading input file ..."):
    with open(_fn_in, "rb") as fo:
      num_accesses = _ReadInt64(fo)
      #Cons.P(num_accesses)
      for i in range(num_accesses):
        tweet_id = _ReadInt64(fo)
        #Cons.P(tweet_id)
        user_id = _ReadInt64(fo)
        #Cons.P(user_id)
        created_at = _ReadStr(fo)
        #Cons.P(created_at)
        lat = _ReadFloat64(fo)
        #Cons.P(lat)
        lon = _ReadFloat64(fo)
        #Cons.P(lon)
        vid = _ReadStr(fo)
        #Cons.P(vid)
        points.append((lon, lat))

  pcs = {}
  for i in range(len(points)):
    pc = PointCluster(i, points[i])
    pcs[i] = pc

  # Make multiple paths, until it stabilizes
  while True:
    pcs1 = _ClusterPointClusters(pcs)
    if len(pcs1) == len(pcs):
      pcs = pcs1
      break
    pcs = pcs1

  max_size = 0
  with open(_fn_plot_data, "w") as fo:
    fo.write("# lat lon num_points_clustered\n")
    for pc_id, pc in pcs.iteritems():
      c = pc.Center()
      fo.write("%f %f %d\n" % (c[1], c[0], pc.Size()))
      max_size = max(max_size, pc.Size())
  Cons.P("Created %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
  Cons.P("Max point cluster size: %d" % max_size)


#def _ReadInt32(fo):
#  b = fo.read(4)
#  return numpy.fromstring(b, dtype=numpy.int32, count=1)


def _ReadInt64(fo):
  b = fo.read(8)
  return numpy.fromstring(b, dtype=numpy.int64, count=1)


def _ReadStr(fo):
  s = _ReadInt64(fo)
  return str(fo.read(s))


def _ReadFloat64(fo):
  b = fo.read(8)
  return numpy.fromstring(b, dtype=numpy.float64, count=1)


def _ClusterPointClusters(pcs):
  with Cons.MTnnl("Clustering point clusters ... "):
    # Point clusters
    #gc {point_cluster_id: PointCluster()}
    new_pcs = {}
    rtree_idx = index.Index()

    for pc_id, pc in pcs.iteritems():
      # Bounding box. It doesn't seem like right need to be bigger than left.
      #gc (left, bottom, right, top)
      cur_pc_bb = pc.BoundingBox()

      if len(new_pcs) == 0:
        new_id = len(new_pcs)
        pc1 = PointCluster(new_id, pc)
        new_pcs[new_id] = pc1
        rtree_idx.insert(new_id, pc1.BoundingBox())
      else:
        nearest_pc_id = None
        for pc_id in rtree_idx.nearest(cur_pc_bb, 1):
          nearest_pc_id = pc_id
          break

        nearest_pc_center_bb = new_pcs[pc_id].BoundingBox()
        dist_sq = (cur_pc_bb[0] - nearest_pc_center_bb[0]) * (cur_pc_bb[0] - nearest_pc_center_bb[0]) \
            + (cur_pc_bb[1] - nearest_pc_center_bb[1]) * (cur_pc_bb[1] - nearest_pc_center_bb[1])
        # Make a new point cluster when it's far enough from each of the
        # center of the point clusters
        if _dist_sq_threshold < dist_sq:
          new_id = len(new_pcs)
          pc1 = PointCluster(new_id, pc)
          new_pcs[new_id] = pc1
          rtree_idx.insert(new_id, pc1.BoundingBox())
        # Add the point cluster to the existing cluster
        else:
          new_pcs[nearest_pc_id].Add(pc)
    print "from %5d to %5d. %5.2f%% reduction" % (len(pcs), len(new_pcs), 100.0 * (len(pcs) - len(new_pcs)) / len(pcs))

    # Re-calculate the centers
    for pc_id, pc in new_pcs.iteritems():
      pc.RecalcCenter()

    return new_pcs


class PointCluster:
  def __init__(self, id, point_or_pc):
    self.id = id

    if type(point_or_pc) is tuple:
      # Bounding box is created using center
      self.points = [point_or_pc]
      self.center = point_or_pc
    else:
      # type(point_or_pc) is PointCluster:
      self.points = point_or_pc.points
      self.center = point_or_pc.center

  def BoundingBox(self):
    return (self.center[0], self.center[1], self.center[0], self.center[1])

  def Add(self, pc):
    self.points.extend(pc.points)

  def Center(self):
    return self.center

  def Size(self):
    return len(self.points)

  def RecalcCenter(self):
    sum_lon = 0.0
    sum_lat = 0.0
    for p in self.points:
      sum_lon += p[0]
      sum_lat += p[1]
    self.center = (sum_lon / len(self.points), sum_lat / len(self.points))


def Plot():
  with Cons.MT("Plotting clustered locations ..."):
    fn_out = "%s.pdf" % _fn_plot_data
    env = os.environ.copy()
    env["FN_IN"] = _fn_plot_data
    env["FN_OUT"] = fn_out
    Util.RunSubp("gnuplot %s/geographic-dist-clustered.gnuplot" % os.path.dirname(__file__), env=env)
    Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


#def PlotUnclustered():
#  with Cons.MT("Plotting un-clustered locations ..."):
#    fn_out = "%s.pdf" % _fn_plot_data
#    env = os.environ.copy()
#    env["FN_IN"] = _fn_plot_data
#    env["FN_OUT"] = fn_out
#    Util.RunSubp("gnuplot %s/fcc-tower-locations.gnuplot" % os.path.dirname(__file__), env=env)
#    Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


if __name__ == "__main__":
  sys.exit(main(sys.argv))

  
# Note: Bulk loading of Rtree index. Not needed for now:
# https://gist.github.com/acrosby/4601257
