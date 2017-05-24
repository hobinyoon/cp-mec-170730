#pragma once

#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point.hpp>

namespace InfraNodes {
	enum NodeType {
		CT,
		AP,
		CDN
	};

	void Load();

	typedef boost::geometry::model::point<double, 2, boost::geometry::cs::cartesian> point;
	double DistToClosest(const NodeType nt, const point& p);
};
