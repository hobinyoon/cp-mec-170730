#!/usr/bin/env python

import math
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
_fn_pnt_clustered_centers = "%s/%s-clustered-centers" % (_dn_result, _fn_in0)


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

			# Make a copy of PCs. ClosestPair() reorders the list.
			pcs0 = list(pcs)
			(distsq, pair) = ClosestPair(pcs0)

			if _clustering_dist_sq_threshold < distsq:
				break

			# Merge the closest pair
			id0 = pair[0].id_
			id1 = pair[1].id_

			# Make sure the data is consistent
			#if (id0 != pcs[id0].id_) or (id1 != pcs[id1].id_):
			#	Cons.P("%d %d" % (id0, id1))
			#	Cons.P("%d %d" % (pcs[id0].id_, pcs[id1].id_))
			#	sys.exit(0)

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

		with open(_fn_pnt_clustered_centers, "w") as fo:
			fmt = "%11.6f %11.6f %3d %3d"
			fo.write(Util.BuildHeader(fmt, "lon lat num_points_clustered cluster_id") + "\n")
			for pc in pcs:
				c = pc.center
				fo.write((fmt + "\n") % (c[0], c[1], len(pc.points), pc.id_))
		Cons.P("Created %s %d" % (_fn_pnt_clustered_centers, os.path.getsize(_fn_pnt_clustered_centers)))

		with open(_fn_pnt_clustered, "w") as fo:
			fmt = "%11.6f %11.6f %3d"
			fo.write(Util.BuildHeader(fmt, "lon lat cluster_id") + "\n")
			for pc in pcs:
				for p in pc.points:
					fo.write((fmt + "\n") % (p[0], p[1], pc.id_))
		Cons.P("Created %s %d" % (_fn_pnt_clustered, os.path.getsize(_fn_pnt_clustered)))


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
			best[1] = (p,q)
			
	# merge two sorted lists by y-coordinate
	def merge(A,B):
		i = 0
		j = 0
		while i < len(A) or j < len(B):
			if (j >= len(B)) or ((i < len(A)) and (A[i].center[1] <= B[j].center[1])):
				yield A[i]
				i += 1
			else:
				yield B[j]
				j += 1

	# Find closest pair recursively; returns all points sorted by y coordinate
	def recur(L0):
		if len(L0) < 2:
			return L0
		split = len(L0)/2
		splitx = L0[split].center[0]
		L0 = list(merge(recur(L0[:split]), recur(L0[split:])))

		# Find possible closest pair across split line
		# Note: this is not quite the same as the algorithm described in class, because
		# we use the global minimum distance found so far (best[0]), instead of
		# the best distance found within the recursive calls made by this call to recur().
		# This change reduces the size of E, speeding up the algorithm a little.
		#
		# Hobin: I think the downside of this is it can't be parallelized. Fine for now.
		E = [p for p in L0 if square(p.center[0]-splitx) < best[0]]
		for i in range(len(E)):
			for j in range(1,8):
				if i+j < len(E):
					testpair(E[i],E[i+j])
		return L0
	
	L.sort()
	recur(L)
	return best


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
		return "%d %s %d\n%s" % (self.id_, self.center, len(self.points), "\n".join(str(i) for i in self.points))

	def Merge(self, pc):
		if True:
			# (Similar) to geographic median
			self.points.extend(pc.points)
			x = []
			y = []
			for p in self.points:
				x.append(p[0])
				y.append(p[1])
			x.sort()
			y.sort()
			if len(x) % 2 == 0:
				i0 = len(x) / 2 - 1
				i1 = i0 + 1
				self.center = ((x[i0] + x[i1]) / 2.0, (y[i0] + y[i1]) / 2.0)
			else:
				i = int(math.floor(len(x) / 2))
				self.center = (x[i], y[i])
		else:
			# Geographic mean

			# Weighted centers
			wc0 = (self.center[0] * len(self.points), self.center[1] * len(self.points))
			wc1 = (pc.center[0] * len(pc.points), pc.center[1] * len(pc.points))
			new_l = len(self.points) + len(pc.points)
			self.center = ((wc0[0] + wc1[0]) / new_l, (wc0[1] + wc1[1]) / new_l)
			self.points.extend(pc.points)


def PlotClustered():
	fn_out = "%s/%s-with-centroids.pdf" % (_dn_result, _fn_in0)

	with Cons.MT("Plotting clustered locations ..."):
		env = os.environ.copy()
		env["FN_IN_PNTS_C"] = _fn_pnt_clustered
		env["FN_IN_PNTS_CC"] = _fn_pnt_clustered_centers
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/access-loc-with-centroids.gnuplot" % os.path.dirname(__file__), env=env, measure_time=True)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


if __name__ == "__main__":
	sys.exit(main(sys.argv))
