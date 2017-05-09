# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

set print "-"

set xdata time
set timefmt "%Y%m"
set format x "'%y"

# Get data range
if (1) {
	set terminal unknown
	plot FN_IN u 1:2 w p
	X_MIN=GPVAL_DATA_X_MIN
	X_MAX=GPVAL_DATA_X_MAX
}

set terminal pdfcairo enhanced size 2.3in, (2.3*0.85)in
set output FN_OUT

set xlabel "Time (year)"
set ylabel "New towers / month" offset -0.8,0

set border back lc rgb "#808080"
set grid xtics ytics back lc rgb "#808080"
set xtics nomirror tc rgb "black" autofreq -10*365.25*24*3600,4*365.25*24*3600
set mxtics 4
set ytics nomirror tc rgb "black" format "10^{%T}" 
set tics back

set logscale y

set xrange[X_MIN:X_MAX]

plot \
FN_IN u 1:2 w lp pt 7 pointsize 0.2 not
