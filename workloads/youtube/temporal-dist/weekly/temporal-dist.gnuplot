# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
WEEKLY_MAX = system("echo $WEEKLY_MAX") + 0
FN_OUT = system("echo $FN_OUT")

set print "-"
#print sprintf("MAX_CLUSTER_SIZE=%f", MAX_CLUSTER_SIZE)

set terminal pdfcairo enhanced size 2.3in, (2.3*0.85)in
set output FN_OUT

set xtics nomirror tc rgb "black" rotate by -45
set ytics nomirror tc rgb "black" autofreq 0,0.2 format "%.1f"
set grid xtics ytics back lc rgb "#808080"
set border back lc rgb "#808080"

set xlabel "Day of week" offset 0,-0.4
set ylabel "Number of accesses\n(relative)" offset 0.5,0

set yrange[0:1]

set xrange[-0.5:6.5]

set bars 4.0

LW=2

plot \
FN_IN u 0:($4/WEEKLY_MAX):($3/WEEKLY_MAX):($7/WEEKLY_MAX):($6/WEEKLY_MAX) w candlesticks lw LW lc rgb "red" not whiskerbars, \
FN_IN u 0:($5/WEEKLY_MAX):($5/WEEKLY_MAX):($5/WEEKLY_MAX):($5/WEEKLY_MAX) w candlesticks lw LW lc rgb "red" not, \
FN_IN u 0:($2/WEEKLY_MAX):($2/WEEKLY_MAX):($2/WEEKLY_MAX):($2/WEEKLY_MAX):xtic(1) w candlesticks lw LW lc rgb "blue" not

# Dow   avg  min  25p  50p  75p  max
# 1       2    3    4    5    6    7

# whisker plot: x  box_min  whisker_min  whisker_high  box_high
