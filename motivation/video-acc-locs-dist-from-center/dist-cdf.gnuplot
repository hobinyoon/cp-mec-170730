#!/usr/bin/gnuplot

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

set terminal pdfcairo enhanced size 2.3in, (2.3*0.85)in
set output FN_OUT

set xlabel "Distance (km)"
set ylabel "CDF" offset 0.8,0

set xtics nomirror tc rgb "black" format "10^{%T}" 
set ytics nomirror tc rgb "black" autofreq 0,0.2 format "%.1f"
set mytics 2
set tics back
set border back lc rgb "#808080"
set grid xtics ytics mytics back lc rgb "#808080"

set logscale x

set xrange [0.1:]
set yrange [0:]

plot FN_IN u ($1/1000.0):2 w l lw 2 not
