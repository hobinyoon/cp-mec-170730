#! /usr/bin/gnuplot

IN_FNS = system("echo $IN_FNS")
IN_DN = system("echo $IN_DN")
OUT_FN = system("echo $OUT_FN")
MAP = "~/work/crawl-twitter/worldmap/world_110m.txt"

set print "-"
#print sprintf("OUT_FN=%s", OUT_FN)

term_width=3.0
set terminal pdfcairo enhanced size term_width in, (term_width*0.8) in
set output OUT_FN

set tmargin screen 0.89

# range_type
# 0: World
# 1: US
# 2: New York
rt=2

if (rt == 0) {
	set xtics nomirror tc rgb "black" autofreq -180,60
	set ytics nomirror tc rgb "black" autofreq -90,30
} else { if (rt == 1) {
	set xtics nomirror tc rgb "black" autofreq -180,30
	set ytics nomirror tc rgb "black" autofreq -90,15
} else { if (rt == 2) {
	set xtics nomirror tc rgb "black" autofreq -180,1
	set ytics nomirror tc rgb "black" autofreq -90,1
} } }

set grid xtics ytics front lc rgb "#808080"
set border back lc rgb "#808080"

if (rt == 0) {
	set xrange[-180:180]
	set yrange[-90:90]
} else { if (rt == 1) {
	set xrange[-130:-60]
	set yrange[20:60]
} else { if (rt == 2) {
	#set xrange[-130:-60]
	#set yrange[20:60]
	set xrange[-75:-70]
	set yrange[40:41.5]
} } }

#do for [i=1:words(IN_FNS)] {
do for [i=1:10] {
	vid = word(IN_FNS, i)[5:15]
	fn = IN_DN . "/" . word(IN_FNS, i)

	set title vid
	# TODO: num_locs(tweets). views. video title.

	plot \
	MAP u 1:2 with filledcurves lw 1 fs solid noborder fc rgb "#F0F0F0" not, \
	fn u 1:2 w p pt 6 pointsize 0.001 lc rgb "red" not
	#print sprintf("%d", i)
}
