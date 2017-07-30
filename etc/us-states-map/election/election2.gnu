#!/usr/bin/gnuplot
#
# Plot a map of the USA together with election results in every state
# and add the state names as labels
#
# AUTHOR: Hagen Wierstorf
# gnuplot 4.6 patchlevel 0

#reset

FN_ELECTION = "election.txt"
FN_USA = "../usa.txt"

# wxt
#set terminal wxt size 350,262 enhanced persist font 'Verdana'
set terminal pdfcairo enhanced size 4.5in,3in
set output "election.pdf"

# png
#set terminal pngcairo size 350,262 enhanced
#set output 'election2.png'

# color definitions
set style line 1 lc rgb '#0088c8' lt 1 lw 0 # --- blue
set style line 2 lc rgb '#cc3333' lt 1 lw 0 # --- red
set style line 3 lc rgb '#ffffff' lt 1 lw 0.5 # --- white

unset key
set border 0
unset tics
set tmargin 0
set bmargin 0
set lmargin 0
set rmargin 0

# get election results for every state
#
# Hobin: Interesting. ELEC becomes an array of 1s and 2s, which is the results
# in each state.
# "stats" can be useful. It could be saved to a separate file and used later.
ELEC=''
stats FN_ELECTION u 1:(ELEC = ELEC.sprintf('%i',($2)))

#set print "-"
#print ELEC

set xrange [-125:-102]    
set yrange [28:50]

# Set x and y have the same unit length.
set size ratio -1

plot for [idx=0:48] FN_USA i idx u 2:1 w filledcurves ls ELEC[idx+1:idx+1],\
                    ''              u 2:1 w l ls 3,\
                    FN_ELECTION     u 6:5:3 w labels tc ls 3
