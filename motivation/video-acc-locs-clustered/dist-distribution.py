#!/usr/bin/env python

import os
import pprint
import sys
import time
from rtree import index

sys.path.insert(0, "%s/work/mutant/ec2-tools/lib/util" % os.path.expanduser("~"))
import Cons
import Util

_fn_in0 = "001-Y4MnpzG5Sqc"
# TODO: what is this in km or mile?
# The clustering assumes a flat earth for a quick insight
_clustering_dist_sq_threshold = 1.5

_dn_in = "%s/data" % os.path.dirname(__file__)
_fn_in_pnts = "%s/%s" % (_dn_in, _fn_in0)

_dn_result = "%s/.result" % os.path.dirname(__file__)
_fn_pnt_clustered = "%s/%s-clustered" % (_dn_result, _fn_in0)


# TODO: draw access locations (red dots), gray lines, then centroids (blue circles)
# You can see how clustering is done


def main(argv):
	Util.MkDirs(_dn_result)

	ClusterPoints()
	PlotClustered()


def ClusterPoints():
	if os.path.isfile(_fn_pnt_clustered):
		return

	points = []
	with Cons.MT("Reading input file %s ..." % _fn_in_pnts):
		with open(_fn_in_pnts) as fo:
			for line in fo.readlines():
				line = line.strip()
				if len(line) == 0:
					continue
				if line[0] == "#":
					continue
				t = line.split()
				if len(t) != 2:
					raise RuntimeError("Unexpected [%s]" % line)
				lon = float(t[0])
				lat = float(t[1])
				points.append((lon, lat))
		Cons.P("%d points" % len(points))

	with Cons.MT("Clustring ..."):
		pcs = {}
		for i in range(len(points)):
			pc = PointCluster(i, points[i])
			pcs[i] = pc

		# Repeat until no more clustering is made
		while True:
			pcs1 = _ClusterPointClusters(pcs)
			if len(pcs1) == len(pcs):
				pcs = pcs1
				break
			pcs = pcs1

		max_size = 0
		for pc_id, pc in pcs.iteritems():
			max_size = max(max_size, pc.Size())
		Cons.P("Max point cluster size: %d" % max_size)

		with open(_fn_pnt_clustered, "w") as fo:
			fo.write("# lat lon num_points_clustered\n")
			for pc_id, pc in pcs.iteritems():
				c = pc.Center()
				fo.write("%f %f %d\n" % (c[1], c[0], pc.Size()))
		Cons.P("Created %s %d" % (_fn_pnt_clustered, os.path.getsize(_fn_pnt_clustered)))


def _ClusterPointClusters(pcs):
	with Cons.MTnnl("Clustering point clusters ... ", print_time=False):
		start_time = time.time()
		# Point clusters
		#   {point_cluster_id: PointCluster()}
		new_pcs = {}
		rtree_idx = index.Index()

		for pc_id, pc in pcs.iteritems():
			# Bounding box. It doesn't seem like right need to be bigger than left.
			#   (left, bottom, right, top)
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
				if _clustering_dist_sq_threshold < dist_sq:
					new_id = len(new_pcs)
					pc1 = PointCluster(new_id, pc)
					new_pcs[new_id] = pc1
					rtree_idx.insert(new_id, pc1.BoundingBox())
				# Add the point cluster to the existing cluster
				else:
					new_pcs[nearest_pc_id].Add(pc)
		dur = time.time() - start_time
		print "from %6d to %5d. %5.2f%% reduction %.0f ms" \
				% (len(pcs), len(new_pcs), 100.0 * (len(pcs) - len(new_pcs)) / len(pcs), (dur * 1000.0))

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


def PlotClustered():
	fn_out = "%s/%s-with-centroids.pdf" % (_dn_result, _fn_in0)

	with Cons.MT("Plotting clustered locations ..."):
		env = os.environ.copy()
		env["FN_IN_PNTS_C"] = _fn_pnt_clustered
		env["FN_IN_PNTS"] = _fn_in_pnts
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/access-loc-with-centroids.gnuplot" % os.path.dirname(__file__), env=env, measure_time=True)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


#def PlotUnclustered():
#	with Cons.MT("Plotting un-clustered locations ..."):
#		fn_out = "%s.pdf" % _fn_pnt_clustered
#		env = os.environ.copy()
#		env["FN_IN"] = _fn_pnt_clustered
#		env["FN_OUT"] = fn_out
#		Util.RunSubp("gnuplot %s/cell-tower-locations.gnuplot" % os.path.dirname(__file__), env=env)
#		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


if __name__ == "__main__":
	sys.exit(main(sys.argv))

	
# Note: Bulk loading of Rtree index. Not needed for now:
# https://gist.github.com/acrosby/4601257
