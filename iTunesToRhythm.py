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
	for song in allRhythmSongs:
		print song.artist + " - " + song.album + " - " + song.title + " - " + song.size
		# find equivalent itunes song
		correlateSongs( song, ituneSparser );

def correlateSongs( song, parser ):
	matches = parser.findSongBySize( song.size );
	for match in matches:
		print "\t found match in " + song.title
	if len(matches) == 0:
		print "\t no matches found"
		
def showUsage():
	print "iTunesToRhythm <path to ItunesMusicLibrary.xml> <path to rhythmdb.xml>"

	
if __name__ == "__main__":
	main(sys.argv)
