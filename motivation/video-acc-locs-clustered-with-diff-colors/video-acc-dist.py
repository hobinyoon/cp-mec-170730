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
_clustering_dist_sq_threshold = 1.0

_dn_in = "%s/data" % os.path.dirname(__file__)
_fn_in_pnts = "%s/%s" % (_dn_in, _fn_in0)

_dn_result = "%s/.result" % os.path.dirname(__file__)
_fn_pnt_clustered = "%s/%s-clustered" % (_dn_result, _fn_in0)

# TODO: Each cluster with different colors


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
		pcs = []
		for i in range(len(points)):
			pc = PointCluster(points[i], i)
			pcs.append(pc)

		while True:
			if len(pcs) % 10 == 0:
				Cons.ClearLine()
				Cons.Pnnl("%d PointClusters" % len(pcs))
			(distsq, pair) = ClosestPair(pcs)
			if _clustering_dist_sq_threshold < distsq:
				break
			# Merge the pair
			id0 = pair[0].id_
			id1 = pair[1].id_
			pcs[id0].Merge(pcs[id1])
			del pcs[id1]
			# Update IDs
			for i in range(len(pcs)):
				pcs[i].id_ = i
		Cons.ClearLine()
		Cons.P("%d PointClusters" % len(pcs))

		max_size = 0
		for pc in pcs:
			max_size = max(max_size, len(pc.points))
		Cons.P("Biggest PointCluster has %d points" % max_size)

		# TODO: coloring
		# TODO: print all points

		with open(_fn_pnt_clustered, "w") as fo:
			fo.write("# lat lon num_points_clustered\n")
			for pc in pcs:
				c = pc.center
				fo.write("%f %f %d\n" % (c[1], c[0], len(pc.points)))
		Cons.P("Created %s %d" % (_fn_pnt_clustered, os.path.getsize(_fn_pnt_clustered)))



#		# {point_cluster_id: PointCluster}
#		# An id is needed for the index.
#		pcs = {}
#		for i in range(len(points)):
#			pc = PointCluster(i, points[i])
#			pcs[i] = pc
#
#		# Repeat until no more clustering is made
#		while True:
#			pcs1 = _ClusterPointClusters(pcs)
#			if len(pcs1) == len(pcs):
#				pcs = pcs1
#				break
#			pcs = pcs1
#
#		max_size = 0
#		for pc_id, pc in pcs.iteritems():
#			max_size = max(max_size, pc.Size())
#		Cons.P("Max point cluster size: %d" % max_size)
#
#		with open(_fn_pnt_clustered, "w") as fo:
#			fo.write("# lat lon num_points_clustered\n")
#			for pc_id, pc in pcs.iteritems():
#				c = pc.Center()
#				fo.write("%f %f %d\n" % (c[1], c[0], pc.Size()))
#		Cons.P("Created %s %d" % (_fn_pnt_clustered, os.path.getsize(_fn_pnt_clustered)))


# This is incorrect. A closest pair may not be next to each other when sorted by x-axis.
#def MergeClosestPair(pcs):
#	with Cons.MT("Merging PointCluster(s) ... "):
#		# Find the closest pair
#
#		# Sweep through from left to write
#		while True:
#			# Sort them by x-cords
#			pcs.sort(key=lambda x: x.center[0])
#
#			Cons.P("Num PointClusters = %d" % len(pcs))
#
#			# Shorted dist squred so far
#			sdists = 180 * 180 + 90 * 90
#			# (index0, index1) of the shortest pair
#			sortest_pair = None
#			for i in range(1, len(pcs)):
#				pc0 = pcs[i - 1]
#				pc1 = pcs[i]
#
#				# Compare y-coords first, which is likely to be farther apart than x-coords
#				y_dist = pc1.center[0] - pc0.center[0]
#				y_dist_sq = y_dist * y_dist
#				if y_dist_sq < sdists:
#					x_dist = pc1.center[1] - pc0.center[1]
#					x_dist_sq = x_dist * x_dist
#					if x_dist_sq < sdists:
#						dist_sq = y_dist_sq + x_dist_sq
#						if dist_sq < sdists:
#							sdists = dist_sq
#							sortest_pair = (i - 1, i)
#			# TODO: Stop merging when sdists is smaller than the threshold.
#			if sdists < shortest_pair is None:
#				break
#			# Merge the two: update the former and delete the latter
#			pcs[shortest_pair[0]].Merge(pcs[shortest_pair[1]])
#			del pcs[shortest_pair[1]]


# https://www.ics.uci.edu/~eppstein/161/python/closestpair.py
#def ClosestPair(L):
#	def square(x): return x*x
#	def sqdist(p,q): return square(p[0]-q[0])+square(p[1]-q[1])
#	
#	# Work around ridiculous Python inability to change variables in outer scopes
#	# by storing a list "best", where best[0] = smallest sqdist found so far and
#	# best[1] = pair of points giving that value of sqdist.  Then best itself is never
#	# changed, but its elements best[0] and best[1] can be.
#	#
#	# We use the pair L[0],L[1] as our initial guess at a small distance.
#	best = [sqdist(L[0],L[1]), (L[0],L[1])]
#	
#	# check whether pair (p,q) forms a closer pair than one seen already
#	def testpair(p,q):
#		d = sqdist(p,q)
#		if d < best[0]:
#			best[0] = d
#			best[1] = p,q
#			
#	# merge two sorted lists by y-coordinate
#	def merge(A,B):
#		i = 0
#		j = 0
#		while i < len(A) or j < len(B):
#			if j >= len(B) or (i < len(A) and A[i][1] <= B[j][1]):
#				yield A[i]
#				i += 1
#			else:
#				yield B[j]
#				j += 1
#
#	# Find closest pair recursively; returns all points sorted by y coordinate
#	def recur(L):
#		if len(L) < 2:
#			return L
#		split = len(L)/2
#		splitx = L[split][0]
#		L = list(merge(recur(L[:split]), recur(L[split:])))
#
#		# Find possible closest pair across split line
#		# Note: this is not quite the same as the algorithm described in class, because
#		# we use the global minimum distance found so far (best[0]), instead of
#		# the best distance found within the recursive calls made by this call to recur().
#		# This change reduces the size of E, speeding up the algorithm a little.
#		#
#		E = [p for p in L if abs(p[0]-splitx) < best[0]]
#		for i in range(len(E)):
#			for j in range(1,8):
#				if i+j < len(E):
#					testpair(E[i],E[i+j])
#		return L
#	
#	L.sort()
#	recur(L)
#	return best[1]


# https://www.ics.uci.edu/~eppstein/161/python/closestpair.py
def ClosestPair(L):
	def square(x): return x*x
	def sqdist(p,q): return square(p.center[0]-q.center[0])+square(p.center[1]-q.center[1])
	
	# Work around ridiculous Python inability to change variables in outer scopes
	# by storing a list "best", where best[0] = smallest sqdist found so far and
	# best[1] = pair of points giving that value of sqdist.  Then best itself is never
	# changed, but its elements best[0] and best[1] can be.
	#
	# We use the pair L[0],L[1] as our initial guess at a small distance.
	best = [sqdist(L[0],L[1]), (L[0],L[1])]
	
	# check whether pair (p,q) forms a closer pair than one seen already
	def testpair(p,q):
		d = sqdist(p,q)
		if d < best[0]:
			best[0] = d
			best[1] = p,q
			
	# merge two sorted lists by y-coordinate
	def merge(A,B):
		i = 0
		j = 0
		while i < len(A) or j < len(B):
			if j >= len(B) or (i < len(A) and A[i].center[1] <= B[j].center[1]):
				yield A[i]
				i += 1
			else:
				yield B[j]
				j += 1

	# Find closest pair recursively; returns all points sorted by y coordinate
	def recur(L):
		if len(L) < 2:
			return L
		split = len(L)/2
		splitx = L[split].center[0]
		L = list(merge(recur(L[:split]), recur(L[split:])))

		# Find possible closest pair across split line
		# Note: this is not quite the same as the algorithm described in class, because
		# we use the global minimum distance found so far (best[0]), instead of
		# the best distance found within the recursive calls made by this call to recur().
		# This change reduces the size of E, speeding up the algorithm a little.
		#
		# Hobin: I think the downside of this is it can't be parallelized. Fine for now.
		E = [p for p in L if abs(p.center[0]-splitx) < best[0]]
		for i in range(len(E)):
			for j in range(1,8):
				if i+j < len(E):
					testpair(E[i],E[i+j])
		return L
	
	L.sort()
	recur(L)
	return (best[0], best[1])




# TODO: Why do you need a dict?
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
	def __init__(self, point, id_):
		self.points = [point]
		self.center = point
		self.id_ = id_

	def __lt__(self, other):
		if self.center[0] < other.center[0]:
			return True
		if self.center[0] > other.center[0]:
			return False
		return (self.center[1] < other.center[1])

	def __repr__(self):
		return "%d %s %d" % (len(self.points), self.center, self.id_)

	def Merge(self, pc):
		# Weighted centers
		wc0 = (self.center[0] * len(self.points), self.center[1] * len(self.points))
		wc1 = (pc.center[0] * len(pc.points), pc.center[1] * len(pc.points))

		new_l = len(self.points) + len(pc.points)

		self.center = ((wc0[0] + wc1[0]) / new_l, (wc0[1] + wc1[1]) / new_l)
		self.points.extend(pc.points)


#class PointCluster:
#	def __init__(self, id, point_or_pc):
#		self.id = id
#
#		if type(point_or_pc) is tuple:
#			# Bounding box is created using center
#			self.points = [point_or_pc]
#			self.center = point_or_pc
#		else:
#			# type(point_or_pc) is PointCluster:
#			self.points = point_or_pc.points
#			self.center = point_or_pc.center
#
#	def BoundingBox(self):
#		return (self.center[0], self.center[1], self.center[0], self.center[1])
#
#	def Add(self, pc):
#		self.points.extend(pc.points)
#
#	def Center(self):
#		return self.center
#
#	def Size(self):
#		return len(self.points)
#
#	def RecalcCenter(self):
#		sum_lon = 0.0
#		sum_lat = 0.0
#		for p in self.points:
#			sum_lon += p[0]
#			sum_lat += p[1]
#		self.center = (sum_lon / len(self.points), sum_lat / len(self.points))


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
