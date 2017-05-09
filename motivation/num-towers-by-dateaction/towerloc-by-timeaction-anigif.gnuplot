# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

set print "-"
print sprintf("FN_IN=%s", FN_IN)
print sprintf("FN_OUT=%s", FN_OUT)

# 65
X_MIN=-130
X_MAX=-65

# 35
Y_MIN=20
Y_MAX=55

set terminal gif animate delay 25 size 1000, 850
set output FN_OUT

set xrange[X_MIN:X_MAX]
set yrange[Y_MIN:Y_MAX]

set border back lc rgb "#808080"
set grid xtics ytics back lc rgb "#808080"
set xtics nomirror tc rgb "black" autofreq -180, 20
set mxtics 2
set ytics nomirror tc rgb "black" autofreq -90, 15
set tics back

PS=0.3
PT=1

# 310078 lines
do for [i=1:310] {
	lineno=i*1000

	set title system("awk '{if (NR == " . lineno . ") printf \"%s/%s/%s %d towers\", substr($1,1,4), substr($1,5,2), substr($1,7,2), NR}' " . FN_IN)

	plot FN_IN u ($0 < (lineno - 1000) ? $2 : 1/0):3 w p pt PT pointsize PS lc rgb "#808080" not, \
		"" u (((lineno - 1000) <= $0 && $0 < lineno) ? $2 : 1/0):3 w p pt PT pointsize PS lc rgb "red" not

	print sprintf("lineno=%d", lineno)
}
