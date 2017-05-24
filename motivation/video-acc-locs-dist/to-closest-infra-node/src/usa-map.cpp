#include <list>
#include <random>
#include <regex>

#include <boost/algorithm/string.hpp>
#include <boost/format.hpp>
#include <boost/polygon/polygon.hpp>

#include "conf.h"
#include "cons.h"
#include "usa-map.h"
#include "util.h"

using namespace std;

// http://www.boost.org/doc/libs/1_61_0/libs/polygon/doc/gtl_custom_polygon.htm

namespace gtl = boost::polygon;
using namespace boost::polygon::operators;

//first lets turn our polygon usage code into a generic
//function parameterized by polygon type
template <typename Polygon>
void test_polygon() {
	//lets construct a 10x10 rectangle shaped polygon
	typedef typename gtl::polygon_traits<Polygon>::point_type Point;

	Point pts[] = {gtl::construct<Point>(0, 0),
		gtl::construct<Point>(10, 0),
		gtl::construct<Point>(10, 10),
		gtl::construct<Point>(0, 10) };

	Polygon poly;
	gtl::set_points(poly, pts, pts+4);

	cout << boost::format("area: %f\n") % gtl::area(poly);
	cout << boost::format("point in polygon: %s\n") % gtl::contains(poly, gtl::construct<Point>(5, 5));
	cout << boost::format("point in polygon: %s\n") % gtl::contains(poly, gtl::construct<Point>(15, 5));
}

//we have to get CPoint working with boost polygon to make our polygon
//that uses CPoint working with boost polygon
namespace boost { namespace polygon {
  template <>
  struct geometry_concept<CPoint> { typedef point_concept type; };
  template <>
  struct point_traits<CPoint> {
    typedef double coordinate_type;

    static inline coordinate_type get(const CPoint& point, 
    orientation_2d orient) {
      if(orient == HORIZONTAL)
        return point.x;
      return point.y;
    }
  };

  template <>
  struct point_mutable_traits<CPoint> {
    typedef double coordinate_type;

    static inline void set(CPoint& point, orientation_2d orient, double value) {
      if(orient == HORIZONTAL)
        point.x = value;
      else
        point.y = value;
    }
    static inline CPoint construct(double x, double y) {
      return CPoint(x, y);
    }
  };
} }

//I'm lazy and use the stl everywhere to avoid writing my own classes
//my toy polygon is a std::list<CPoint>
typedef std::list<CPoint> CPolygon;

//we need to specialize our polygon concept mapping in boost polygon
namespace boost { namespace polygon {
  //first register CPolygon as a polygon_concept type
  template <>
  struct geometry_concept<CPolygon>{ typedef polygon_concept type; };

  template <>
  struct polygon_traits<CPolygon> {
    typedef double coordinate_type;
    typedef CPolygon::const_iterator iterator_type;
    typedef CPoint point_type;

    // Get the begin iterator
    static inline iterator_type begin_points(const CPolygon& t) {
      return t.begin();
    }

    // Get the end iterator
    static inline iterator_type end_points(const CPolygon& t) {
      return t.end();
    }

    // Get the number of sides of the polygon
    static inline std::size_t size(const CPolygon& t) {
      return t.size();
    }

    // Get the winding direction of the polygon
    static inline winding_direction winding(const CPolygon& t) {
      return unknown_winding;
    }
  };

  template <>
  struct polygon_mutable_traits<CPolygon> {
    //expects stl style iterators
    template <typename iT>
    static inline CPolygon& set_points(CPolygon& t, 
                                       iT input_begin, iT input_end) {
      t.clear();
      t.insert(t.end(), input_begin, input_end);
      return t;
    }

  };
} }


struct BoundingBox {
	float x0; float x1;
	float y0; float y1;

	BoundingBox(const vector<CPoint>& pts) {
		bool first = true;
		for (const auto& p: pts) {
			if (first) {
				x0 = x1 = p.x;
				y0 = y1 = p.y;
				first = false;
			} else {
				if (p.x < x0) {
					x0 = p.x;
				} else if (x1 < p.x) {
					x1 = p.x;
				}
				if (p.y < y0) {
					y0 = p.y;
				} else if (y1 < p.y) {
					y1 = p.y;
				}
			}
		}
	}

	bool Contains(float lon, float lat) {
		return ((x0 <= lon) && (lon <= x1) && (y0 <= lat) && (lat <= y1));
	}
};


namespace UsaMap {
	// Polygons of all states
	vector<CPolygon> _polygons;
	vector<BoundingBox> _bboxes;

	void Load() {
		const string fn = Conf::GetFn("usa_map");
		Cons::MT _(boost::format("Loading the USA map from %s ...") % fn);

		vector<CPoint> pts;

		ifstream ifs(fn);
		for (string line; getline(ifs, line); ) {
			boost::trim_right(line);
			if (line.size() == 0 || line[0] == '#') {
				// Finish a polygon
				if (pts.size() > 0) {
					CPolygon poly;
					gtl::set_points(poly, pts.begin(), pts.end());
					_polygons.push_back(poly);
					_bboxes.push_back(BoundingBox(pts));
					pts.clear();
				}
				continue;
			}

			// line contains coordinates
			static const auto sep = boost::is_any_of(" ");
			vector<string> t;
			boost::split(t, line, sep, boost::token_compress_on);
			if (t.size() != 2)
				THROW(boost::format("Unexpected: %s") % line);
			double lat = atof(t[0].c_str());
			double lon = atof(t[1].c_str());
			pts.push_back(gtl::construct<CPoint>(lon, lat));
		}

		// Finish the last polygon
		if (pts.size() > 0) {
			CPolygon poly;
			gtl::set_points(poly, pts.begin(), pts.end());
			_polygons.push_back(poly);
			_bboxes.push_back(BoundingBox(pts));
			pts.clear();
		}

		Cons::P(boost::format("Loaded %d polygons") % _polygons.size());
	}

	bool Contains(double lon, double lat) {
		for (size_t i = 0; i < _polygons.size(); i ++) {
			// Check first if the point is contained in the bounding box of the polygon
			if (_bboxes[i].Contains(lon, lat)) {
				auto pnt = gtl::construct<CPoint>(lon, lat);
				if (gtl::contains(_polygons[i], pnt))
					return true;
			}
		}
		return false;
	}

	random_device _rd;
	CPoint GenRandPntInUsa() {
		mt19937 gen(_rd());

		uniform_real_distribution<double> urd_lon(-127, -65);
		uniform_real_distribution<double> urd_lat(23, 50);

		while (true) {
			double lon = urd_lon(gen);
			double lat = urd_lat(gen);
			if (Contains(lon, lat)) {
				//Cons::P(boost::format("%f %f Y") % lon % lat);
				return CPoint(lon, lat);
			} else {
				//Cons::P(boost::format("%f %f") % lon % lat);
			}
		}
	}

	void Test() {
		mt19937 gen(_rd());
		//uniform_real_distribution<double> urd_lon(-180, 180);
		//uniform_real_distribution<double> urd_lat(-90, 90);
		uniform_real_distribution<double> urd_lon(-127, -65);
		uniform_real_distribution<double> urd_lat(23, 50);

		vector<double> lons;
		vector<double> lats;

		int num_points = 1000;
		for (int i = 0; i < num_points; i ++) {
			lons.push_back(urd_lon(gen));
			lats.push_back(urd_lat(gen));
		}

		Cons::MT _(boost::format("Testing %d points ...") % num_points);

		int in = 0;
		int out = 0;
		for (int i = 0; i < num_points; i ++) {
			double lon = lons[i];
			double lat = lats[i];
			if (Contains(lon, lat)) {
				//cout << boost::format("%f %f 1\n") % lon % lat << flush;
				in ++;
			} else {
				//cout << boost::format("%f %f 0\n") % lon % lat << flush;
				out ++;
			}
		}
		Cons::P(boost::format("%d points in, %d points out") % in % out);
	}
};
