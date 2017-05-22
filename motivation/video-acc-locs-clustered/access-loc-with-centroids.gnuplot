#!/usr/bin/gnuplot

FN_IN_PNTS_C = system("echo $FN_IN_PNTS_C")
FN_IN_PNTS = system("echo $FN_IN_PNTS")
MAP = "~/work/castnet/misc/us-states-map/usa.txt"
FN_OUT = system("echo $FN_OUT")

set terminal pdfcairo enhanced size 3.0in, (3.0*0.75)in
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
set grid xtics ytics front lc rgb "#808080"
set border back lc rgb "#808080"

set nokey

plot \
MAP u 2:1 with filledcurves lw 1 fs solid noborder fc rgb "#F0F0F0" not, \
MAP u 2:1 with l lw 1 lc rgb "#E0E0E0" not, \
FN_IN_PNTS u 1:2 w p pt 7 pointsize 0.1 lc rgb "red" not, \
FN_IN_PNTS_C u 2:1 w p pt 6 pointsize 0.2 lc rgb "blue" not, \
FN_IN_PNTS_C u 2:1:3 w labels offset 0,-0.3 font ",5" tc rgb "blue" not
