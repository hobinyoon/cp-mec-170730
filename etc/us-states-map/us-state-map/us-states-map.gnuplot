#!/usr/bin/gnuplot

FN_USA = "../usa.txt"

set terminal pdfcairo enhanced size 4.5in,3in
set output "us-states.pdf"

unset key
unset border
unset tics

set tmargin 0
set bmargin 0
set lmargin 0
set rmargin 0

# 70
set xrange[-125:-66.5]

# 35
set yrange[24:49.5]

plot FN_USA u 2:1 w l lw 1 lc rgb "#808080"
