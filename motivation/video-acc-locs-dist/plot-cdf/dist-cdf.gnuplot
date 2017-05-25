#!/usr/bin/gnuplot

FN_CC = system("echo $FN_CC")
FN_CT = system("echo $FN_CT")
FN_AP= system("echo $FN_AP")
STAT_CT  = system("echo $STAT_CT")
STAT_AP  = system("echo $STAT_AP")
STAT_CDN = system("echo $STAT_CDN")
FN_CDN = system("echo $FN_CDN")
FN_OUT = system("echo $FN_OUT")

set print "-"

set terminal pdfcairo enhanced size 2.3in, (2.3*0.85)in
set output FN_OUT

set xlabel "Distance (m)"
set ylabel "CDF" offset 0.8,0

set xtics nomirror tc rgb "black" format "10^{%T}" 
set mxtics 10
set ytics nomirror tc rgb "black" autofreq 0,0.2 format "%.1f"
set mytics 2
set tics back
set border back lc rgb "#808080"
set grid xtics ytics mytics back lc rgb "#808080"

set logscale x

X_MIN=10
set xrange [X_MIN:50000000]
set yrange [0:]

titles = "CT AP CDN"
do for [i=1:words(titles)] {
	title_ = word(titles, i)

	if (title_ eq "CT") {
		s = STAT_CT
	} else { if (title_ eq "AP") {
		s = STAT_AP
	} else { if (title_ eq "CDN") {
		s = STAT_CDN
	} } }

	avg = word(s, 1) + 0.0
	# 1p and 99p
	x_l = word(s, 2) + 0.0
	x_r = word(s, 3) + 0.0
	_y = word(s, 4) + 0.0

	# OL: orthogonal lines
	# HB: horizontal bar with 1p, avg, and 99p
	style_ = "OL"
	#style_ = "HB"

	if (style_ eq "OL") {
		LW1 = 6
		set arrow from avg,0 to avg,1.0 nohead lc rgb "blue" lw LW1 lt 0
		if (_y != -1) {
			set obj circle at avg, _y size 1.2 fs solid fc rgb "blue" front
		}
		print sprintf("%s %f %f", title_, avg, _y)

		if (title_ eq "CT") {
			set label title_ at avg,_y right offset -1,0
		} else { if (title_ eq "AP") {
			set label title_ at avg,_y left offset 1,0
		} else { if (title_ eq "CDN") {
			set label title_ at avg,0.5 right offset -1,0
		} } }

		#if (_y == -1) {
		#	set arrow from avg,0 to avg,1.0 nohead lc rgb "blue" lw LW1 lt 0
		#} else {
		#	set arrow from avg,0 to avg,_y nohead lc rgb "blue" lw LW1 lt 0
		#	set arrow from X_MIN,_y to avg,_y nohead lc rgb "blue" lw LW1 lt 0
		#}
	} else {
		LW1 = 3
		# Wing height
		WH=0.02
		set arrow from x_l,_y to x_r,_y nohead lc rgb "blue" lw LW1
		set obj circle at avg, _y size 1.2 fs solid fc rgb "blue" front
		set arrow from x_l,_y-WH to x_l,_y+WH nohead lc rgb "blue" lw LW1
		set arrow from x_r,_y-WH to x_r,_y+WH nohead lc rgb "blue" lw LW1
		set label title_ at x_r,_y offset 1,0
	}
}

LW=3

plot \
FN_CC u 1:2 w l lw LW lc rgb "red" not, \

# Move factor along x-axis and y-axis
#mx=1.3
#my=0.02
#FN_CC u ((CT0 <= $1 && $1 <= CT1) ? $1/mx : 1/0):($2 + my) w l lw LW lc rgb "blue" not

#FN_CT u 1:2 w l lw 2 t "CT", \
#FN_AP u 1:2 w l lw 2 t "AP", \
#FN_CDN u 1:2 w l lw 2 t "CDN", \
