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
	print "Using RhythmBox database " + args[1]

	#open the libraries
	rhythmParser = RhythmLibraryParser(args[1]);
	itunesParser = iTunesLibraryParser(args[0]);
	allRhythmSongs = rhythmParser.getSongs()
	
	# go through each song in rhythmbox
	correlator = SongCorrelator(itunesParser)
	for song in allRhythmSongs:
		print song.artist + " - " + song.album + " - " + song.title + " - " + song.size
		# find equivalent itunes song
		match = correlator.correlateSong( song, options.confirm, options.promptForDisambiguate )
		# update database, if match
		if match != None and options.writeChanges == True:
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
	options, args = parser.parse_args()
	
	# check that files are specified
	if len(args) != 2:
		parser.error( "you must supply 2 files names" )
	return options, args

class SongCorrelator:
	def __init__(self, parser ):
		self.parser = parser
		self.zeroMatches = 0
		self.fullMatches = 0
		self.ambiguousMatches = 0;


	# attempt to find matching song in database
	def correlateSong( self, song, confirm, promptForDisambiguate ):
		match = None
		matches = self.parser.findSongBySize( song.size );
		matchcount = len(matches)
		
		# no results
		if matchcount == 0:
			print "\t no matches found"
			self.zeroMatches = self.zeroMatches + 1
		# full match
		elif matchcount == 1:
			match = matches[0]
			if match.title == song.title:
				print "\t 100% match on " + self.dumpMatch( match )
				self.fullMatches = self.fullMatches + 1
			else:
				match = self.disambiguate( song, matches, promptForDisambiguate )
		# ambiguous match
		elif matchcount > 1:
			print "\t multiple matches"
			for match in matches:
				print "\t\t " + self.dumpMatch( match )
			# attempt a resolution
			match = self.disambiguate( song, matches, promptForDisambiguate )
			# unsuccessful attempt, record ambiguity
			if match == None:
				self.ambiguousMatches = self.ambiguousMatches + 1
		#review
		if confirm == True:
			foo = raw_input( 'press <enter> to continue')
			
		#done
		return match

	def dumpMatch(  self, match ):
		return match.title + ", rating = " + str(match.rating)
			
	def disambiguate(self,song,matches,prompt):
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
		
		if prompt == True:
			print "\t\t cannot disambiguate.  Please select file or press <Enter> for no match:"
			numMatch = 0
			for match in matches:
				numMatch = numMatch + 1
				print "\t\t\t\t[" + str(numMatch) + "] " + self.dumpMatch(match)
				
			selection = self.inputNumber("\t\t\t\t? ")
			if selection > 0:
				return matches[selection - 1]
			
		return None
	
	def inputNumber(self, msg):
		result = raw_input(msg)
		if len(result) == 0:
			return 0
		try:
			resultNum = int(result)
			
			if resultNum < min or resultNum > max:
				print "out of range"
				return self.inputNumber( msg )
				
			return resultNum
		except:
			print "invalid input"
			return self.inputNumber(msg)
		
	
if __name__ == "__main__":
	main(sys.argv)
