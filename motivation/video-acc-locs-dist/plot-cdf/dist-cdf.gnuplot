#!/usr/bin/gnuplot

FN_CC = system("echo $FN_CC")
FN_CT = system("echo $FN_CT")
FN_AP= system("echo $FN_AP")
FN_CDN = system("echo $FN_CDN")
FN_OUT = system("echo $FN_OUT")

set terminal pdfcairo enhanced size 2.3in, (2.3*0.85)in
set output FN_OUT

set xlabel "Distance (m)"
set ylabel "CDF" offset 0.8,0

set xtics nomirror tc rgb "black" format "10^{%T}" 
set ytics nomirror tc rgb "black" autofreq 0,0.2 format "%.1f"
set mytics 2
set tics back
set border back lc rgb "#808080"
set grid xtics ytics mytics back lc rgb "#808080"

set logscale x

set xrange [10:]
set yrange [0:]

plot \
FN_CC u 1:2 w l lw 2 t "CC", \
FN_CT u 1:2 w l lw 2 t "CT", \
FN_AP u 1:2 w l lw 2 t "AP", \
FN_CDN u 1:2 w l lw 2 t "CDN", \
