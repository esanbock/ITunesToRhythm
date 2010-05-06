#!/usr/bin/env python2.3
#
#  iTunesToRhythm.py
#  
#
#

import sys
import libxml2
from optparse import OptionParser
from dumprhythm import RhythmLibraryParser, RhythmSong
from dumpitunes import iTunesLibraryParser, iTunesSong


def main(argv):
	# process command line
	options, args = processCommandLine(argv)
	print "Reading iTunes database from " + args[0]
	print "Reading RhythmBox database from " + args[1]

	#open the libraries
	rhythmParser = RhythmLibraryParser(args[0]);
	itunesParser = iTunesLibraryParser(args[1]);
	allRhythmSongs = rhythmParser.getSongs()
	
	# go through each song in rhythmbox
	correlator = SongCorrelator(itunesParser, options.c, options.d)
	for song in allRhythmSongs:
		print song.artist + " - " + song.album + " - " + song.title + " - " + song.size
		# find equivalent itunes song
		match = correlator.correlateSong( song )
		# update database, if match
		if len(match) > 0 and options.w == True:
				song.setRating( match.Rating / 20 )
		
	# dump summary results
	print "full matches = " + str( correlator.fullMatches )
	print "zero matches = " + str( correlator.zeroMatches )
	print "ambiguous matches = " + str( correlator.ambiguousMatches )

def processCommandLine( argv ):
	parser = OptionParser("iTunesToRhythm [options] <path to ItunesMusicLibrary.xml> <path to rhythmdb.xml>")
	parser.add_option("-c", "--confirm", action="store_true", dest="confirm", default = False, help="confirm every match" )
	parser.add_option("-w", "--writechanges", action="store_true", dest="writeChanges", default = False, help="write changes to destination file" )
	parser.add_option("-d", "--disambiguate", action="store_true", dest="promptForDisambiguate", default = False, help="prompt user to resolve ambiguities" )
	options, args = options.parse_args()
	
	# check that files are specified
	if len(args) <> 2
		parser.error( "you must supply 2 files names" )
	return options, args

class SongCorrelator:
	def __init__(self, parser, confirm = False, promptForDisambiguate = False ):
		self.parser = parser
		self.zeroMatches = 0
		self.fullMatches = 0
		self.ambiguousMatches = 0;

	# attempt to find matching song in database
	def correlateSong( self, song ):
		matches = self.parser.findSongBySize( song.size );
		matchcount = len(matches)
		
		# no results
		if matchcount == 0:
			print "\t no matches found"
			self.zeroMatches = self.zeroMatches + 1
		# full match
		elif matchcount == 1 and match.title == song.title:
			print "\t 100% match on " + dumpMatch( match )
			self.fullMatches = self.fullMatches + 1
		# ambiguous match
		elif matchcount > 1:
			print "\t multiple matches"
			for match in matches:
				print "\t\t " + dumpMatch( match )
			# attempt a resolution
			match = disambiguate( song, matches, promptForDisambiguate )
			# unsuccessful attempt, record ambiguity
			if len(match == 0):
				self.ambiguousMatches = self.ambiguousMatches + 1
		#review
		if confirm == True:
			input('press <enter> to continue')
			
		#done
		return match

	def dumpMatch(  self, match ):
		return match.title + ", rating = " + str(match.rating)
			
	def disambiguate(self,song,matches,prompt=false):
		# attempt to disambiguate by title
		print "\t looking for secondary match on title"
		titlematchcount = 0
		for match in matches:
			if match.title == song.title:
				titlematchcount = titlematchcount + 1
				latstitlematch = match
				
		if titlematchcount == 1:
			# we successfully disambiguated using the title
			print "\t\t disambiguated using title"
			self.fullMatches = self.fullMatches + 1
			return latstitlematch
		
		if prompt == true:
			print "\t\t cannot disambiguate.  Please select file or press <Enter> for no match:"
			numMatch = 0
			for match in matches:
				numMatch = numMatch + 1
				print "[" + str(numMatch) + "] " + dumpMatch(match)
			selection = input("?")
			if len(selection)  > 0
				return matches[selection]
			
		return None
		
	
if __name__ == "__main__":
	main(sys.argv)
