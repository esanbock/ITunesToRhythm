#!/usr/bin/env python2.3
#
#  iTunesToRhythm.py
#  
#
#  Created by esanbockd on 5/6/10.
#  Copyright (c) 2010 __MyCompanyName__. All rights reserved.
#

import sys
import libxml2
from dumprhythm import RhythmLibraryParser, RhythmSong
from dumpitunes import iTunesLibraryParser, iTunesSong


def main(argv):
	# check params
	if len(argv) != 3:
		print "ERROR:  incorrect number of parameters.  Expected 2, received " + str(len(argv) - 1)
		showUsage();
		return -1;
	
	iTunesLocation = argv[1]
	rhythmLocation = argv[2]
	print "Reading iTunes database from " + iTunesLocation
	print "Reading RhythmBox database from " + rhythmLocation

	#open the libraries
	rhythmParser = RhythmLibraryParser(rhythmLocation);
	itunesParser = iTunesLibraryParser(iTunesLocation);
	allRhythmSongs = rhythmParser.getSongs()
	
	# go through each song in rhythmbox
	correlator = SongCorrelator(itunesParser)
	for song in allRhythmSongs:
		print song.artist + " - " + song.album + " - " + song.title + " - " + song.size
		# find equivalent itunes song
		correlateSong( song )
		
	# dump summary results
	print "full matches = " + str( correlator.fullMatches )
	print "zero matches = " + str( correlator.zeroMatches )
	print "ambiguous matches = " + str( correlator.ambiguousMatches )

class SongCorrelator:
	def __init__(self, parser ):
		self.parser = parser
		self.zeroMatches = 0
		self.fullMatches = 0
		self.ambiguousMatches = 0;

	def correlateSong( self, song ):
		matches = self.parser.findSongBySize( song.size );
		matchcount = 0
		for match in matches:
			matchcount = matchcount + 1
			
		if matchcount == 0:
			print "\t no matches found"
			self.zeroMatches = self.zeroMatches + 1
			return
			
		if matchcount == 1 && match.title == song.title:
			print "\t 100% match on " match.title + ", rating = " + str(match.rating)
			self.fullMatches + self.fullMatches + 1
			return match
	
		if matchcount > 1
			print "\t multiple matches"
			for match in matches:
				print match.title + ", rating = " + str(match.rating)
			self.ambiguousMatches = self.ambiguousMatches + 1
		
def showUsage():
	print "iTunesToRhythm <path to ItunesMusicLibrary.xml> <path to rhythmdb.xml>"

	
if __name__ == "__main__":
	main(sys.argv)
