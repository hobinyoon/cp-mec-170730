#!/usr/bin/gnuplot
#
# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

LatLngRatio=1.5

LAT_0=22
LAT_1=50

# Latitute range of YouTube request locations
LAT_YT_0=24.5
LAT_YT_1=49

LAT_D=LAT_1-LAT_0

#set terminal pdfcairo enhanced size 4.5in, (4.5 * LAT_D / 70 * LatLngRatio)in
set terminal pdfcairo enhanced size 2.3in, (2.3*0.85)in
set output FN_OUT

set noborder
set notics
#set xtics nomirror scale 0,0 font ",10" format "%.0f{/Symbol \260}" tc rgb "#808080" autofreq -90,30,-30
#set ytics nomirror scale 0,0 font ",10" format "%.0f{/Symbol \260}" tc rgb "#808080" autofreq -90,15

set lmargin 0
set rmargin 0
set tmargin 0
set bmargin 0

# 70
#set xrange[-130:-60]
# 30
#set yrange[LAT_0:LAT_1]

# 60
set xrange[-126:-66]
# 35
set yrange[20.5:49.5]

set key below

circle_size_0(s)=sqrt(s)/20.0

circle_size(x, y, s)= y < LAT_YT_0 ? 1/0 : (\
	y > LAT_YT_1 ? 1/0 : (circle_size_0(s)))

# Core and edge data centers are plotted twice to get the label order right,
# but they can go away when the legend is plotted differently.
plot \
"../us-states-map/usa.txt" u 2:1 with filledcurves lw 1 fs solid border lc rgb "#808080" fc rgb "#FFFFFF" not, \
FN_IN u 2:1 w points pt 7 pointsize 0.015 lc rgb "#FF0000" t "Cellular tower"
