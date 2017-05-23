#!/usr/bin/gnuplot

FN_IN_PNTS_C = system("echo $FN_IN_PNTS_C")
FN_IN_PNTS_CC = system("echo $FN_IN_PNTS_CC")
MAP = "~/work/castnet/misc/us-states-map/usa.txt"
FN_OUT = system("echo $FN_OUT")

set terminal pdfcairo enhanced size 3.0in, (3.0*0.75)in
#set terminal pdfcairo enhanced size 3.0in, (3.0*0.40)in
set output FN_OUT

# 62
X_MIN=-127
X_MAX=-65
set xrange[X_MIN:X_MAX]
# 32
set yrange[23:50]

TTC = "#808080"
set xtics nomirror tc rgb TTC autofreq -180,10
set ytics nomirror tc rgb TTC autofreq -90,5
#set mxtics 10
#set mytics 5
#set grid xtics mxtics ytics mytics front lt 1 lc rgb "#808080"
set grid xtics ytics front lc rgb "#808080"
set border back lc rgb "#808080"

set nokey

set palette model RGB defined (\
  0 "#0000FF" \
, 1 "#8A2BE2" \
, 2 "#A52A2A" \
, 3 "#5F9EA0" \
, 4 "#008B8B" \
, 5 "#006400" \
, 6 "#483D8B" \
, 7 "#DAA520" \
)

# https://www2.uni-hamburg.de/Wiss/FB/15/Sustainability/schneider/gnuplot/colors.htm
# blueviolet    "#8A2BE2"
# brown         "#A52A2A"
# cadetblue     "#5F9EA0"
# darkcyan      "#008B8B"
# darkgreen     "#006400"
# darkslateblue "#483D8B"
# goldenrod     "#DAA520"

unset colorbox

mod(a, b)=a-(floor(a/b)*b)

plot \
MAP u 2:1 with filledcurves lw 1 fs solid noborder fc rgb "#FCFCFC" not, \
MAP u 2:1 with l lw 1 lc rgb "#E0E0E0" not, \
FN_IN_PNTS_C  u 1:2:(0.25):(mod($3,8)) w circles fs transparent solid 0.3 noborder palette not, \
FN_IN_PNTS_CC u 1:2 w p pt 1 pointsize 0.15 lc rgb "red" not, \

#FN_IN_PNTS_CC u 1:2:3 w labels offset 0,-0.3 font ",5" tc rgb "blue" not

# FN_IN_PNTS_C  u 1:2:(mod($3,8)) w p pt 7 pointsize 0.1 palette not, \
# FN_IN_PNTS_CC u 1:2 w p pt 6 pointsize 0.15 lc rgb "red" not, \
