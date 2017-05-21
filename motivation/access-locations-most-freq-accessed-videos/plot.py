#!/usr/bin/env python

import locale
import os
import re
import sys

sys.path.insert(0, "%s/work/mec-node-placement/etc" % os.path.expanduser("~"))
import Cons
import Util


_dn_acc_loc = "%s/gen-data/.result/acc-locs" % os.path.dirname(__file__)

def main(argv):
	GenInputFiles(_dn_acc_loc)

	locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

	# {video_id: VideoInfo}
	vid_vi = GetVideoInfo()

	vids = []
	view_cnts = []
	titles = []
	num_tweets = []
	for fn in _in_fns:
		vid = fn[4:]
		if vid not in vid_vi:
			raise RuntimeError("Unexpected")
		vids.append(vid)
		view_cnts.append(locale.format("%d", int(vid_vi[vid].view_cnt), grouping=True))
		titles.append(vid_vi[vid].title)
		num_tweets.append(locale.format("%d", GetNumTweets(fn), grouping=True))

	dn_out = "%s/.result" % os.path.dirname(__file__)
	Util.MkDirs(dn_out)

	fn_out = "%s/youtube-video-acc-locs.pdf" % dn_out

	with Cons.MT("Plotting YouTube video access locations ..."):
		env = os.environ.copy()
		env["IN_FNS"] = " ".join(_in_fns)
		env["IN_DN"] = _dn_acc_loc
		env["VIDS"] = " ".join(vids).replace("_", "\\_")
		env["VIEW_CNTS"] = " ".join(view_cnts)
		env["NUM_TWEETS"] = " ".join(num_tweets)
		for i in range(len(titles)):
			# Limit the title to 80 chars
			env["TITLE%d" % (i+1)] = titles[i][0:80].replace("_", "\\_")
		env["OUT_FN"] = fn_out
		Util.RunSubp("gnuplot %s/loc.gnuplot" % os.path.dirname(__file__), env=env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


_in_fns = []

def GenInputFiles(dn):
	global _in_fns

	ranks = []
	for fn in os.listdir(dn):
		#Cons.P(fn)
		mo = re.match(r"(?P<rank>\d\d\d)-(\d|\w|-){11}", fn)
		if mo is not None:
			ranks.append(int(mo.group("rank")))
			_in_fns.append(fn)
		else:
			Cons.P(fn)

	ranks.sort()
	_in_fns.sort()

	all_exists = True
	if len(ranks) != 100:
		all_exists = False

	if all_exists:
		for i in range(1, 100+1):
			if ranks[i - 1] != i:
				Cons.P("file starting with %d doesn't exist" % i)
				all_exists = False
				break
	
	if all_exists:
		return

	raise RuntimeError("Implement calling the data generator")


def GetVideoInfo():
	vid_vi = {}
	fn = "%s/work/crawl-twitter/tools/get-youtube-video-details/get-youtube-video-details/video-info-concise" % os.path.expanduser("~")
	with open(fn) as fo:
		for line in fo:
			t = re.split(r" +", line.strip())
			# chZmtjD8rxw 1154       5142   hd    PT5M49S M.O.D. - I Got Bitches
			if len(t) < 6:
				raise RuntimeError("Unexpected")
			vid = t[0]
			view_cnt = t[2]
			title = " ".join(t[5:])
			vid_vi[vid] = VideoInfo(view_cnt, title)
	return vid_vi


def GetNumTweets(fn0):
	fn = "%s/%s" % (_dn_acc_loc, fn0)
	num_tweets = 0
	with open(fn) as fo:
		for line in fo:
			if len(line) == 0:
				continue
			if line[0] == "#":
				continue
			num_tweets += 1
	return num_tweets


class VideoInfo:
	def __init__(self, view_cnt, title):
		self.view_cnt = view_cnt
		self.title = title


if __name__ == "__main__":
	sys.exit(main(sys.argv))
