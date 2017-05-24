#pragma once

struct CPoint {
	double x;
	double y;
	CPoint(double x_, double y_)
		: x(x_), y(y_)
	{}
};

namespace UsaMap {
	void Load();
	//bool Contains(double lat, double lon);
	CPoint GenRandPntInUsa();
	void Test();
};
