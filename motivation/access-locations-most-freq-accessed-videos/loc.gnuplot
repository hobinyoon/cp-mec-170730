#! /usr/bin/gnuplot

IN_FNS = system("echo $IN_FNS")
IN_DN = system("echo $IN_DN")
OUT_FN = system("echo $OUT_FN")
MAP = "~/work/crawl-twitter/worldmap/world_110m.txt"

set print "-"
#print sprintf("OUT_FN=%s", OUT_FN)

term_width=3.0
set terminal pdfcairo enhanced size term_width in, (term_width*0.7) in
set output OUT_FN

set xtics nomirror tc rgb "black" autofreq -180,60
set ytics nomirror tc rgb "black" autofreq -90,30
set grid xtics ytics back lc rgb "#808080"
set border back lc rgb "#808080"

set xrange[-180:180]
set yrange[-90:90]

#do for [i=1:words(IN_FNS)] {
do for [i=1:10] {
	vid = word(IN_FNS, i)[5:15]
	fn = IN_DN . "/" . word(IN_FNS, i)

	set title vid
	# TODO: num_locs(tweets). views. video title.

	plot \
	MAP u 1:2 with filledcurves lw 1 fs solid noborder fc rgb "#F0F0F0" not, \
	fn u 1:2 w p pt 7 pointsize 0.1 lc rgb "red" not
	#print sprintf("%d", i)
}
