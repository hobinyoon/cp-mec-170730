# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_DATEACTION_YEARMONTH = system("echo $FN_DATEACTION_YEARMONTH")
FN_NUM_NEW              = system("echo $FN_NUM_NEW")
FN_NUM_TOTAL            = system("echo $FN_NUM_TOTAL")
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

if (1) {
	do for [i=1:words(FN_DATEACTION_YEARMONTH)] {
		ym = word(FN_DATEACTION_YEARMONTH, i)

		num_new = word(FN_NUM_NEW, i) + 0
		num_total = word(FN_NUM_TOTAL, i) + 0

		set title sprintf("%s new_nodes=%05d total_nodes=%06d", ym, num_new, num_total)

		plot FN_IN u ($0 < (num_total - num_new) ? $2 : 1/0):3 w p pt PT pointsize PS lc rgb "#808080" not, \
			"" u (((num_total - num_new) <= $0 && $0 < num_total) ? $2 : 1/0):3 w p pt PT pointsize PS lc rgb "red" not

		print sprintf("ym=%s", ym)
	}
}

if (0) {
	# 19960723 -85.684444 38.195833
	# 20161217 -83.971917 33.611722

	do for [y=1996:2016] {
		if (y == 1996) {
			m0 = 7
		} else {
			m0 = 1
		}

		do for [m=m0:12] {
			ym = y * 10000 + m * 100
			print sprintf("ym=%d", ym)
			set title sprintf("%d/%02d", y, m)
			plot FN_IN u ($1 < ym ? $2 : 1/0):3 w p pt PT pointsize PS lc rgb "#808080" not, \
				"" u ((ym <= $1 && $1 < (ym + 100)) ? $2 : 1/0):3 w p pt PT pointsize PS lc rgb "red" not, \
			# Not sure how to plot the number of nodes here
			# Preprocess in Python
		}
	}
}


if (0) {
	# 310078 lines
	do for [i=1:310] {
		lineno=i*1000

		set title system("awk '{if (NR == " . lineno . ") printf \"%s/%s/%s %d towers\", substr($1,1,4), substr($1,5,2), substr($1,7,2), NR}' " . FN_IN)

		plot FN_IN u ($0 < (lineno - 1000) ? $2 : 1/0):3 w p pt PT pointsize PS lc rgb "#808080" not, \
			"" u (((lineno - 1000) <= $0 && $0 < lineno) ? $2 : 1/0):3 w p pt PT pointsize PS lc rgb "red" not

		print sprintf("lineno=%d", lineno)
	}

	# Note: Towards the end, there are days with more than 1000 new towers in a day.
	#   When you plot 1000 towers at a time, there appears vertical strips since records are sorted by ts first and then latitude.
	#     To remove them, the order can be randomized. Not a big deal until they need to be presented.
}
