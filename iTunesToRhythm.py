#!/usr/bin/env python
#
#Copyright @ 2010 Douglas Esanbock
#iTunesToRhythm is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License, or
#(at your option) any later version.
#
#iTunesToRhythm is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with iTunesToRhythm; if not, write to the Free Software Foundation, Inc.,
#51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA

import sys
import platform

if platform.system() == "Darwin":
	sys.path.append('/sw/lib/python2.5/site-packages/')
	from dumpitunesmac import iTunesMacParser, iTunesMacSong

import libxml2
import linecache
from optparse import OptionParser,  OptionGroup

def main(argv):
	# process command line
	options, args = processCommandLine(argv)
	try:
		print "Reading input from " + args[0]
		inputParser = getParser(args[0], options)
		print "Writing to output " + args[1]
		destinationParser = getParser(args[1], options)
	except UnrecognizedFormatException as err:
		print "\tFile format unrecognized.  Details - [" + err.value + "]"
		return -1
	except IOError as badio:
		print "\tUnable to open file. " + str(badio)
		return -2
	#retrieve destination songs
	allDestinationSongs = destinationParser.getSongs()

	# go through each song in destination library
	correlator = SongCorrelator(inputParser)
	for song in allDestinationSongs:
                try: 
                        print song.artist + " - " + song.album + " - " + song.title + " - " + str(song.size)
                except UnicodeEncodeError as charError:
                        print "*** UNICODE *** "
		if song.size is not None and song.size != "Unknown":
			# find equivalent itunes song
			match = correlator.correlateSong(song, options.confirm, options.fastAndLoose,  options.promptForDisambiguate)
			# update database, if match
			if match is not None and options.writeChanges:
				if not options.noratings:
					song.setRating(match.rating)
					print "\t\t\tRating changed to " + str(match.rating)
				if not options.noplaycounts:
					song.setPlaycount(match.playcount)
					print "\t\t\tPlay count changed to " + str(match.playcount)

	# dump summary results
	print "\nSummary\n------------------------------------"
	print "manually resolved matches = " + str(correlator.manuallyResolvedMatches)
	print "full matches = " + str(correlator.fullMatches)
	print "partial matches = " + str(correlator.partialMatches)
	print "no matches = " + str(correlator.zeroMatches)
	print "unresolved ambiguous matches = " + str(correlator.ambiguousMatches)

	# save
	if options.writeChanges:
		destinationParser.save()
		print "Changes were written to destination"
	else:
		print "Changes were not written to destination \n\tuse -w to actually write changes to disk"

def getParser(file_,  options):
	if file_ == "mysql":
		print "\tassuming amarok database"
		return AmarokLibraryParser(options.servername, options.database, options.username,  options.password)
	if file_ == "itunes":
		print "\tassuming itunes on the mac"
		from dumpamarok import AmarokLibraryParser, AmarokSong
		return iTunesMacParser()
	if file_ == "wmp":
                print "\tassuming Windows Media Player"
                from dumpwmp import WMPParser
                return WMPParser();

	desc = linecache.getline(file_,  2)
	if desc== '':
		raise IOError("File not found")
	if desc.find("Apple Computer") != -1:
		#open itunes linbrary
		print "\tdetected Itunes library"
		from dumpitunes import iTunesLibraryParser, iTunesSong
		return iTunesLibraryParser(file_)
	if desc.find("rhythmdb") != -1:
		print "\tdetected Rhythm box library"
		from dumprhythm import RhythmLibraryParser, RhythmSong
		return RhythmLibraryParser(file_)
		
	raise UnrecognizedFormatException(desc)

def processCommandLine(argv):
	parser = OptionParser("iTunesToRhythm [options] <inputfile>|itunes|mysql <outputfile>|mysql|itunes")
	parser.add_option("-c", "--confirm", action="store_true", dest="confirm", default = False, help="confirm every match")
	parser.add_option("-w", "--writechanges", action="store_true", dest="writeChanges", default = False, help="write changes to destination file")
	parser.add_option("-a", "--disambiguate", action="store_true", dest="promptForDisambiguate", default = False, help="prompt user to resolve ambiguities")
	parser.add_option("-l",  "--fastandloose", action="store_true", dest= "fastAndLoose",  default = False,  help = "ignore differences in files name when a file size match is made against  a single song.   Will not resolve multiple matches")
	parser.add_option("--noplaycounts", action="store_true", dest= "noplaycounts",  default = False,  help = "do not update play counts")
	parser.add_option("--noratings", action="store_true", dest= "noratings",  default = False,  help = "do not update ratings")

	amarokGroup = OptionGroup(parser,  "Amarok options",  "Options for connecting to an Amarok MySQL remote database")
	amarokGroup.add_option("-s",  "--server",  dest="servername",  help = "host name of the MySQL database server")
	amarokGroup.add_option("-d",  "--database",  dest="database",  help = "database name of the amarok database")
	amarokGroup.add_option("-u",  "--username",  dest="username",  help = "login name of the amarok database")
	amarokGroup.add_option("-p",  "--password",  dest="password",  help = "password of the user")

	parser.add_option_group(amarokGroup)
	# parse options
	options, args = parser.parse_args()

	# check that files are specified
	if len(args) != 2:
			parser.print_help()
			parser.error("you must supply 2 file names or 1 file name and the word mysql followed by database information.  Specyfing itunes will use a running instance of iTunes on the Mac")

	# make surce source & destination are not the same
	if args[0] == args[1]:
		parser.error("source and destination cannot be the same")

	# we're ok
	return options, args

class SongCorrelator(object):
	def __init__(self, parser):
		self.parser = parser
		self.zeroMatches = 0
		self.fullMatches = 0
		self.ambiguousMatches = 0
		self.partialMatches = 0
		self.manuallyResolvedMatches = 0

	# attempt to find matching song in database
	def correlateSong(self, song, confirm, fastAndLoose,  promptForDisambiguate):
		match = None
		matches = self.parser.findSongBySize(song.size)
		matchcount = len(matches)

		# no results
		if matchcount == 0:
			print "\t no matches found"
			self.zeroMatches = self.zeroMatches + 1
		# full match
		elif matchcount == 1:
			match = matches[0]
			if match.title == song.title:
				print "\t 100% match on " + self.dumpMatch(match)
				self.fullMatches = self.fullMatches + 1
			else:
				if not fastAndLoose:
					match = self.disambiguate(song, matches, promptForDisambiguate)
				else:
					print "\t 50% match on " + self.dumpMatch(match)
					self.partialMatches = self.partialMatches + 1
		# multiple matches
		else:
			print "\t multiple matches"
			for match in matches:
				print "\t\t " + self.dumpMatch(match)
			# attempt a resolution
			match = self.disambiguate(song, matches, promptForDisambiguate)

		#review
		if confirm:
			foo = raw_input('press <enter> to continue, Ctrl-C to cancel')

		#done
		return match

	def dumpMatch(self, match):
		return match.title + ", playcount = " + str(match.playcount) + ", rating = " + str(match.rating)

	def disambiguate(self, song, matches, prompt):
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

		if prompt:
			print "\t\t cannot disambiguate.  Trying to match " + song.filePath
			print "Please select file or press <Enter> for no match:"
			numMatch = 0
			for match in matches:
				numMatch = numMatch + 1
				print "\t\t\t\t[" + str(numMatch) + "] " + self.dumpMatch(match) + ", " + match.filePath

			selection = self.inputNumber("\t\t\t\t? ", 1, len(matches))
			if selection > 0:
				self.manuallyResolvedMatches = self.manuallyResolvedMatches + 1
				return matches[selection - 1]

		# user did not select, record ambiguity
		self.ambiguousMatches = self.ambiguousMatches + 1
		return None

	def inputNumber(self, msg, min_, max_):
		result = raw_input(msg)
		if len(result) == 0:
			return 0
		try:
			resultNum = int(result)

			if resultNum < min_ or resultNum > max_:
				print "out of range"
				return self.inputNumber(msg, min_, max_)

			return resultNum
		except ValueError:
            # int() failed
			print "invalid input"
			return self.inputNumber(msg, min_, max_)

class UnrecognizedFormatException( Exception ):
	def __init__(self, line):
		self.value = line
	def str(self):
		return repr(self.value)		



if __name__ == "__main__":
	main(sys.argv)
