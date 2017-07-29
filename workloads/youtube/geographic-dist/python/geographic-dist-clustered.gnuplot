#!/usr/bin/gnuplot
#
# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

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

# 60
set xrange[-126:-66]
# 35
set yrange[20.5:49.5]

circle_size_0(s)=sqrt(s)/60.0

circle_size_2(s)=sqrt(s)/80.0
circle_size_1(s)=s<=5 ? circle_size_2(5) : circle_size_2(s)

circle_size(s)=s<20 ? circle_size_1(s) : circle_size_0(s)

#set xrange[-126:-66]
x0=-96
y0=24
#set label "Cellular towers" at -96, 24 center

# Legend
#   Note: max_cluster_size can be parameterized later
max_cluster_size=460
x1=x0-24
#y1=y0-2.2
y1=y0-1.5

s=5
set obj circle at x1,y1 size circle_size(20) fs transparent solid 0.7 noborder fc rgb "red"
set label (sprintf("< %d", s)) at x1,y1 left offset 0.9,0 tc rgb "black"

x1=x1+10
s=50
set obj circle at x1,y1 size circle_size(s) fs transparent solid 0.7 noborder fc rgb "red"
set label (sprintf("%d", s)) at x1,y1 left offset 0.9,0 tc rgb "black"

x1=x1+10
s=100
set obj circle at x1,y1 size circle_size(s) fs transparent solid 0.7 noborder fc rgb "red"
set label (sprintf("%d", s)) at x1,y1 left offset 0.9,0 tc rgb "black"

x1=x1+10
s=200
set obj circle at x1,y1 size circle_size(s) fs transparent solid 0.7 noborder fc rgb "red"
set label (sprintf("%d", s)) at x1,y1 left offset 0.9,0 tc rgb "black"

x1=x1+10
s=max_cluster_size
set obj circle at x1,y1 size circle_size(s) fs transparent solid 0.7 noborder fc rgb "red"
set label (sprintf("%d", s)) at x1,y1 left offset 0.9,0 tc rgb "black"

set nokey

# Core and edge data centers are plotted twice to get the label order right,
# but they can go away when the legend is plotted differently.
plot \
"../us-states-map/usa.txt" u 2:1 with filledcurves lw 1 fs solid border lc rgb "#808080" fc rgb "#FFFFFF" not, \
FN_IN u 2:($3 <  20 ? $1 : 1/0):(circle_size_1($3)) w p pt 7 pointsize variable lc rgb "#FF7070" not, \
FN_IN u 2:($3 >= 20 ? $1 : 1/0):(circle_size_0($3)) w circles fs transparent solid 0.7 noborder lc rgb "#FF0000" t "Cellular towers", \

#FN_IN u 2:($3 <  10 ? $1 : 1/0) w p pt 7 pointsize 0.1 lc rgb "#FF8080" not, \
