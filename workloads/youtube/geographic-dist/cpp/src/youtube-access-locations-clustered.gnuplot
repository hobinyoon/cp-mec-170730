# Tested with gnuplot 4.6 patchlevel 4

FN_IN = system("echo $FN_IN")
MAX_CLUSTER_SIZE = system("echo $MAX_CLUSTER_SIZE") + 0
FN_OUT = system("echo $FN_OUT")

set print "-"
print sprintf("FN_IN=%s", FN_IN)
print sprintf("MAX_CLUSTER_SIZE=%d", MAX_CLUSTER_SIZE)
print sprintf("FN_OUT=%s", FN_OUT)

set terminal pdfcairo enhanced size 2.3in, (2.3*0.85)in
set output FN_OUT

set noborder
set notics
#set xtics nomirror scale 0,0 font ",10" format "%.0f{/Symbol \260}" tc rgb "#808080" autofreq -90,30,-30
#set ytics nomirror scale 0,0 font ",10" format "%.0f{/Symbol \260}" tc rgb "#808080" autofreq -90,15

set lmargin 0
set rmargin 0
set tmargin 0
set bmargin 0

# 60
set xrange[-126:-66]
# 35
set yrange[20.5:49.5]

circle_size_0(s)=sqrt(s)/100.0
circle_size(s)=s<20 ? circle_size_0(s) : circle_size_0(s)

#set xrange[-126:-66]
x0=-96
y0=24
#set label "Cellular towers" at -96, 24 center

# Legend
x1=x0-25
y1=y0-1.5

s=10
set obj circle at x1,y1 size circle_size(40) fs transparent solid 0.9 noborder fc rgb "red"
set label (sprintf("< %d", s)) at x1,y1 left offset 0.5,0 tc rgb "black" font ",9"

x1=x1+8
s=100
set obj circle at x1,y1 size circle_size(s) fs transparent solid 0.9 noborder fc rgb "red"
set label (sprintf("%d", s)) at x1,y1 left offset 0.5,0 tc rgb "black" font ",9"

x1=x1+8
s=1000
set obj circle at x1,y1 size circle_size(s) fs transparent solid 0.5 noborder fc rgb "red"
set decimal locale
set label (sprintf("%'g", s)) at x1,y1 left offset 0.5,0 tc rgb "black" font ",9"

x1=x1+10
s=10000
set obj circle at x1,y1 size circle_size(s) fs transparent solid 0.5 noborder fc rgb "red"
set label (sprintf("%'g", s)) at x1,y1 left offset 0.8,0 tc rgb "black" font ",9"

x1=x1+14
s=MAX_CLUSTER_SIZE
set obj circle at x1,y1 size circle_size(s) fs transparent solid 0.5 noborder fc rgb "red"
set label (sprintf("%'g", s)) at x1,y1 left offset 2.0,0 tc rgb "black" font ",9"

set nokey

set style fill transparent solid 0.35 noborder

# Core and edge data centers are plotted twice to get the label order right,
# but they can go away when the legend is plotted differently.
plot \
"../us-states-map/usa.txt" u 2:1 with filledcurves lw 1 fs solid border lc rgb "#808080" fc rgb "#FFFFFF" not, \
FN_IN u 1:($3 <  20 ? $2 : 1/0):(circle_size($3)) w p pt 7 pointsize variable lc rgb "#FF7070" not, \
FN_IN u 1:($3 >= 20 ? $2 : 1/0):(circle_size($3)) w circles fs transparent solid 0.5 noborder lc rgb "#FF0000" t "Cellular towers", \

#FN_IN u 2:($3 <  10 ? $1 : 1/0) w p pt 7 pointsize 0.1 lc rgb "#FF8080" not, \
