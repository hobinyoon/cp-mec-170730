import csv
import os
import pprint
import re
import sys

sys.path.insert(0, "%s/work/mutant/ec2-tools/lib/util" % os.path.expanduser("~"))
import Cons
import Util

import Conf
import TowermapCsv


def GetNumTowersByTimeActions():
	fn_in = GetTsCoord()
	fn_out = "%s/num-towers-by-timeaction" % Conf.dn_result

	if os.path.isfile(fn_out):
		return fn_out

	with Cons.MT("Generating num towers by ts range ..."):
		# Group by date_aciton year-month
		da_num = {}

		# ts_begin, ts_end, num
		with open(fn_in) as fo:
			for line in fo:
				#Cons.P(line)
				t = line.split(" ")
				if len(t) != 3:
					raise RuntimeError("Unexpected: [%s]" % line)
				# date_action
				da = t[0]
				#lon = t[1]
				#lat = t[2]

				#year = da[0:4]
				#month = da[4:6]
				ym = da[0:6]

				if ym in da_num:
					da_num[ym] += 1
				else:
					da_num[ym] = 1

		#Cons.P(pprint.pformat(da_num))
		fmt = "%6s %6d %6d"
		with open(fn_out, "w") as fo:
			fo.write(Util.BuildHeader(fmt, "year_month num_towers num_towers_culumated") + "\n")
			num_total = 0
			for ym, num in sorted(da_num.iteritems()):
				num_total += num
				fo.write((fmt + "\n") % (ym, num, num_total))
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))
		return fn_out


# line number for the beginning of a new month and the beginning of the next month
# total number of nodes.
# number of new nodes in the month.
def GetTsCoordMeta():
	fn = GetTsCoord()

	# Group by date_aciton year-month
	da_num = {}

	with open(fn) as fo:
		for line in fo:
			#Cons.P(line)
			t = line.split(" ")
			if len(t) != 3:
				raise RuntimeError("Unexpected: [%s]" % line)
			# date_action
			da = t[0]
			#lon = t[1]
			#lat = t[2]

			#year = da[0:4]
			#month = da[4:6]
			ym = da[0:6]

			if ym in da_num:
				da_num[ym] += 1
			else:
				da_num[ym] = 1

	arr_da = []
	arr_num_new = []
	arr_num_total = []
	num_total = 0
	for ym, num_new in sorted(da_num.iteritems()):
		num_total += num_new
		#Cons.P("%s %d %d" % (ym, num_new, num_total))
		arr_da.append(ym)
		arr_num_new.append(num_new)
		arr_num_total.append(num_total)
	return (arr_da, arr_num_new, arr_num_total)


def GetTsCoord():
	fn_towermap_csv = TowermapCsv.GetFile()
	fn_out = "%s/towers-ts-coord" % Conf.dn_result

	if os.path.isfile(fn_out):
		return fn_out

	with Cons.MT("Generating ts coord file ..."):
		out_lines = []
		with open(fn_towermap_csv, "rb") as fo:
			cr = csv.reader(fo, delimiter=",", quotechar="\"")
			i = 0
			num_nulls = 0
			for row in cr:
				i += 1

				if i == 1:
					#Cons.P(row)
					continue
				if i == 2:
					continue
				# latitude, CO_EN_Reg_Number, ID, Company, Address, city, Field22, Field23, email, longitude, RA_Reg_Number, date_action, agl, ground, type, faa, ID1
				#        0                 1   2        3        4     5        6        7      8          9             10           11   12      13    14   15   16
				# ['4.6770000000000003e+01', '1000001', '172295', 'Drinker Biddle & Reath LLP', '1500 K Street, NW, Suite 1100', 'Washington', '', '', 'elizabeth.hammond@dbr.com', '-1.1202361111111099e+02', '1000001', '01/28/05 00:00:00', '4.6600000000000001e+01', '1.5097000000000000e+03', 'TOWER', 'N/A', '2']

				lat = row[0]
				lon = row[9]

				# data_action
				# 01/28/05 00:00:00
				# 01234567890123456
				da = row[11]

				if len(lat) == 0 or len(lon) == 0 or len(da) == 0:
					num_nulls += 1
					continue

				mo = re.match(r"\d\d\/\d\d\/\d\d 00:00:00", da)
				if mo is None:
					raise RuntimeError("Unexpected")

				# year month day
				year = int(da[6:8])
				if year < 30:
					year += 2000
				else:
					year += 1900
				da = "%d%s%s" % (year, da[0:2], da[3:5])

				lat = float(lat)
				lon = float(lon)
				out_lines.append("%s %f %f" % (da, lon, lat))
		Cons.P("num_nulls=%d (%.2f%%)" % (num_nulls, 100.0 * num_nulls / i))
		Cons.P("total_num_towers_after_filtering_out_nulls=%d" % i)

		out_lines.sort()
		with open(fn_out, "w") as fo:
			for l in out_lines:
				fo.write("%s\n" % l)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))
		return fn_out
