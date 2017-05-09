# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

set print "-"
print sprintf("FN_IN=%s", FN_IN)
print sprintf("FN_OUT=%s", FN_OUT)

#set xdata time
#set timefmt "%Y%m"
#set format x "'%y"

# Get data range to fix the range during the multi plot
if (0) {
	# Not good actually. There seems to be null entries, making the coordinates 0
	#   X_MIN=-176.705472 X_MAX=0.000000 Y_MIN=0.000000 Y_MAX=71.310361
	set terminal unknown
	plot \
	FN_IN u 2:3 w p
	X_MIN=GPVAL_DATA_X_MIN
	X_MAX=GPVAL_DATA_X_MAX
	Y_MIN=GPVAL_DATA_Y_MIN
	Y_MAX=GPVAL_DATA_Y_MAX
	print sprintf("X_MIN=%f X_MAX=%f Y_MIN=%f Y_MAX=%f", X_MIN, X_MAX, Y_MIN, Y_MAX)
} else {
	# 65
	X_MIN=-130
	X_MAX=-65

	# 35
	Y_MIN=20
	Y_MAX=55
}

set terminal pdfcairo enhanced size 2.3in, (2.3*0.85)in
set output FN_OUT

set xrange[X_MIN:X_MAX]
set yrange[Y_MIN:Y_MAX]

set border back lc rgb "#808080"
set grid xtics ytics back lc rgb "#808080"
set xtics nomirror tc rgb "black" autofreq -180, 20
set mxtics 2
set ytics nomirror tc rgb "black" autofreq -90, 15
set tics back


do for [t=1997:2016] {
	set title sprintf("Year %d", t)
	plot FN_IN u ($1 <= (t * 10000) ? $2 : 1/0):3 w p pt 7 pointsize 0.3 not

	# TODO: new ones too
}





if (0) {
set border back lc rgb "#808080"
set grid xtics ytics back lc rgb "#808080"
set xtics nomirror tc rgb "black" autofreq -10*365.25*24*3600,4*365.25*24*3600
set mxtics 4
set ytics nomirror tc rgb "black" format "10^{%T}" 
set tics back

set logscale y

set xrange[X_MIN:X_MAX]

set title "Number of new towers"

plot \
FN_IN u 1:2 w lp pt 7 pointsize 0.2 not

set title "Total number of towers"
set ylabel "# of towers"

plot \
FN_IN u 1:3 w l lw 4 not
}
