#! /usr/bin/gnuplot

# Plot most popular one only. For paper.
PLOT_MOSTPOPULAR_SMALL = system("echo $PLOT_MOSTPOPULAR_SMALL") + 0

IN_FNS = system("echo $IN_FNS")
IN_DN = system("echo $IN_DN")
VIDS = system("echo $VIDS")
VIEW_CNTS = system("echo $VIEW_CNTS")
NUM_TWEETS = system("echo $NUM_TWEETS")
OUT_FN = system("echo $OUT_FN")

set print "-"
#print sprintf("PLOT_MOSTPOPULAR_SMALL=%d", PLOT_MOSTPOPULAR_SMALL)
#print sprintf("OUT_FN=%s", OUT_FN)

if (PLOT_MOSTPOPULAR_SMALL) {
	term_width=2.5
} else {
	term_width=3.0
	set tmargin screen 0.92
}
set terminal pdfcairo enhanced size term_width in, (term_width*0.8) in
set output OUT_FN


# range_type
# 0: World
# 1: US
# 2: New York
rt=1

# Tick text color
if (PLOT_MOSTPOPULAR_SMALL) {
	TTC = "#808080"
} else {
	TTC = "black"
}

if (rt == 0) {
	set xtics nomirror tc rgb TTC autofreq -180,60
	set ytics nomirror tc rgb TTC autofreq -90,30
	MAP = "~/work/crawl-twitter/worldmap/world_110m.txt"
} else { if (rt == 1) {
	set xtics nomirror tc rgb TTC autofreq -180,10
	set ytics nomirror tc rgb TTC autofreq -90,5
	MAP = "~/work/castnet/misc/us-states-map/usa.txt"
} else { if (rt == 2) {
	set xtics nomirror tc rgb TTC autofreq -180,1
	set ytics nomirror tc rgb TTC autofreq -90,1
	MAP = "~/work/castnet/misc/us-states-map/usa.txt"
} } }

set grid xtics ytics front lc rgb "#808080"
set border back lc rgb "#808080"

if (rt == 0) {
	set xrange[-180:180]
	set yrange[-90:90]
} else { if (rt == 1) {
	set xrange[-127:-66]
	set yrange[23:50]
} else { if (rt == 2) {
	#set xrange[-130:-60]
	#set yrange[20:60]
	set xrange[-75:-70]
	set yrange[40:41.5]
} } }

if (PLOT_MOSTPOPULAR_SMALL) {
	num_plots = 1
} else {
	num_plots = words(IN_FNS)
}

do for [i=1:num_plots] {
	vid = word(VIDS, i)
	view_cnt = word(VIEW_CNTS, i)
	num_tweets = word(NUM_TWEETS, i)
	vtitle = system("echo $TITLE".i)

	if (PLOT_MOSTPOPULAR_SMALL) {
		PS=0.10
	} else {
		set title view_cnt . " " . num_tweets . " " . vid . "\n" . vtitle font ",6" offset 0,-1.5
		PS=0.006
	}

	fn = IN_DN . "/" . word(IN_FNS, i)

	if (rt == 0) {
		plot MAP u 1:2 with filledcurves lw 1 fs solid noborder fc rgb "#F0F0F0" not, \
			fn u 1:2 w p pt 6 pointsize 0.001 lc rgb "red" not
	} else { if (rt >= 1) {
		plot MAP u 2:1 with filledcurves lw 1 fs solid noborder fc rgb "#F0F0F0" not, \
			MAP u 2:1 with l lw 1 lc rgb "#E0E0E0" not, \
			fn u 1:2 w p pt 7 pointsize PS lc rgb "red" not
	} }

	print sprintf("%d", i)
}
