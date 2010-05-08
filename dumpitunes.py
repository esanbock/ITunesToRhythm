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
#along with Rhythmbox; if not, write to the Free Software Foundation, Inc.,
#51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA

import sys
import libxml2
from songparser import BaseSong, BaseLibraryParser

class iTunesSong( BaseSong ):
	def __init__(self, song):
		self.artist = song.xpathEval("string[preceding-sibling::* = 'Artist']")
		self.album = song.xpathEval("string[preceding-sibling::* = 'Album']")
		self.title = song.xpathEval("string[preceding-sibling::* = 'Name']")[0].content
		self.size = song.xpathEval("integer[preceding-sibling::* = 'Size']")
		self.rating = song.xpathEval("integer[preceding-sibling::* = 'Rating']")
		self.playcount = song.xpathEval("integer[preceding-sibling::* = 'Play Count']")
		self.filePath = song.xpathEval("string[preceding-sibling::* = 'Location']")[0].content
		
		if len(self.artist) == 0:
			self.artist = "Unknown"
		else:
			self.artist = self.artist[0].content

		if len(self.album) == 0:
			self.album = "Unknown"
		else:
			self.album = self.album[0].content
		
		if len(self.size) == 0:
			self.size = "Unknown"
		else:
			self.size = self.size[0].content
			
		if len(self.rating) == 0:
			self.rating = 0
		else:
			self.rating = int(self.rating[0].content)

		if len(self.playcount) == 0:
			self.playcount = 0
		else:
			self.playcount = int(self.playcount[0].content)

def main(argv):
	location = argv[1]
	print "Reading iTunes library from " + location
	parser = iTunesLibraryParser(location);
	allSongs = parser.getSongs( )
	for song in allSongs:
		print song.artist + " - " + song.album + " - " + song.title + " - " + song.size

class iTunesLibraryParser( BaseLibraryParser ):
	def getSongs(self):
		allSongNodes = self.xpathContext.xpathEval("/plist/dict/dict/dict/*/..")
		allSongs = []
		for songNode in allSongNodes:
		        itunesSong = iTunesSong( songNode )
			allSongs.append( itunesSong )
		return allSongs
	
	def findSongBySize( self, size ):
		matches = self.xpathContext.xpathEval("/plist/dict/dict/dict[integer = '" + str(size) + "']")
		matchingsongs = []
		for match in matches:
			song = iTunesSong( match )
			matchingsongs.append( song )
		return matchingsongs
		
if __name__ == "__main__":
        main(sys.argv)

