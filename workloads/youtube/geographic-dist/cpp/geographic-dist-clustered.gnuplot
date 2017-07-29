#!/usr/bin/gnuplot
#
# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
MAX_CLUSTER_SIZE = system("echo $MAX_CLUSTER_SIZE") + 0.0
FN_OUT = system("echo $FN_OUT")
US_STATES_MAP = "~/work/cp-mec/etc/us-states-map/usa.txt"

set print "-"
print sprintf("MAX_CLUSTER_SIZE=%f", MAX_CLUSTER_SIZE)

set terminal pdfcairo enhanced size 3.2in, 2.3in
set output FN_OUT

set noborder
set notics
if (0) {
  set xtics nomirror scale 0,0 font ",10" format "%.0f{/Symbol \260}" tc rgb "#808080" autofreq -90,30,-30
  set ytics nomirror scale 0,0 font ",10" format "%.0f{/Symbol \260}" tc rgb "#808080" autofreq -90,15
}

set lmargin 0
set rmargin 0
set tmargin 0
set bmargin 0

# 60
set xrange[-126:-66]
# 34
set yrange[22.5:50.5]

set size 0.78, 1

# Curve the color and size so that the big clusters are more noticeable.
color_1(s) = (s/MAX_CLUSTER_SIZE) ** 0.0001
size_1(s) = 0.15 * ((s/MAX_CLUSTER_SIZE) ** 0.15)

num_colors=1000
set palette maxcolors num_colors
set palette model RGB defined (\
  0                  "blue", \
  num_colors * 1 / 3 "green", \
  num_colors * 2 / 3 "yellow", \
  num_colors         "red")

set cbtics ( \
  sprintf("%.0f", MAX_CLUSTER_SIZE) color_1(MAX_CLUSTER_SIZE) \
  ,                         "10000" color_1(10000) \
  ,                          "1000" color_1( 1000) \
  ,                           "100" color_1(  100) \
  ,                            "10" color_1(   10) \
  ,                             "1" color_1(    1) \
)

set colorbox user origin 0.82, 0.1 size 0.025, 0.85
#set colorbox origin screen 0.9, screen 0.9

plot \
US_STATES_MAP u 2:1 w filledcurves lw 1 fs solid border lc rgb "#808080" fc rgb "#FFFFFF" not, \
FN_IN u 1:2:(size_1($3)):(color_1($3)) w p pt 7 ps variable palette not, \

# "with points" makes about 1/5 smaller file size than "with circles"

# Map adds 160K to the output pdf size
#US_STATES_MAP u 2:1 w filledcurves lw 1 fs solid border lc rgb "#808080" fc rgb "#FFFFFF" not, \
