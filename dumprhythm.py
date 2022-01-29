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
import libxml2
from songparser import BaseSong, BaseLibraryParser

class RhythmSong(BaseSong):
	def __init__(self, node):
		self.xmlNode = node
		self.artist = self.xmlNode.xpathEval("artist")[0].content
		self.album = self.xmlNode.xpathEval("album")[0].content
		self.title = self.xmlNode.xpathEval("title")[0].content
		self.size = self.xmlNode.xpathEval("file-size")[0].content
		self.filePath = self.xmlNode.xpathEval("location")[0].content
		self.playcount = self.xmlNode.xpathEval("play-count")
		self.rating = self.xmlNode.xpathEval("rating")
		self.dateadded = self.xmlNode.xpathEval("first-seen")[0].content
		self.playdate = self.xmlNode.xpathEval("last-played")

		if len(self.playcount) == 0:
			self.playcount = 0
		else:
			self.playcount = int(self.playcount[0].content)

		if len(self.rating) == 0:
			self.rating = 0
		else:
			self.rating = int(round(float(self.rating[0].content))) * 20

		if len(self.dateadded) == 0:
			self.dateadded = 0
		else:
			self.dateadded = int(self.dateadded)

		if len(self.playdate) == 0:
			self.playdate = 0
		else:
			self.playdate = int(self.playdate)


	def setRating(self, rating):
		ratingNode = self.xmlNode.xpathEval("rating")
		if len(ratingNode) == 0:
			newNode = libxml2.newNode("rating")
			newNode.setContent(str(rating / 20))
			self.xmlNode.addChild(newNode)
		else:
			ratingNode[0].text = str(rating / 20)

	def setPlaycount(self, playcount):
		playcountNode = self.xmlNode.xpathEval("play-count")
		if len(playcountNode) == 0:
			newNode = libxml2.newNode("play-count")
			newNode.setContent(str(playcount))
			self.xmlNode.addChild(newNode)
		else:
			playcountNode[0].setContent(str(playcount))

	def setDateAdded(self, dateadded):
		dateaddedNode = self.xmlNode.xpathEval("first-seen")
		if len(dateaddedNode) == 0:
			newNode = libxml2.newNode("first-seen")
			newNode.setContent(str(dateadded))
			self.xmlNode.addChild(newNode)
		else:
			dateaddedNode[0].setContent(str(dateadded))

	def setPlayDate(self, playdate):
		playdateNode = self.xmlNode.xpathEval("last-played")
		if len(playdateNode) == 0:
			newNode = libxml2.newNode("last-played")
			newNode.setContent(str(playdate))
			self.xmlNode.addChild(newNode)
		else:
			playdateNode[0].setContent(str(playdate))

def main(argv):
	location = argv[1]
	print( "Reading database from " + location )
	parser = RhythmLibraryParser(location)
	allSongs = parser.getSongs()
	for song in allSongs:
		try:
			print( song.artist + " - " + song.album + " - " + song.title + " - " + song.size )
		except UnicodeEncodeError as charError:
			print( "*** UNICODE *** " )

class RhythmLibraryParser(BaseLibraryParser):
	def getSongs(self):
		allSongNodes = self.doc.xpathEval("//entry[@type='song']")
		return [RhythmSong(s) for s in allSongNodes]

	def findSongBySize(self, size):
		matches = self.doc.xpathEval("//entry[@type='song' and file-size = '" + str(size)  + "']")
		matchingsongs = []
		for match in matches:
			song = RhythmSong(match)
			matchingsongs.append(song)
		return matchingsongs

if __name__ == "__main__":
	main(sys.argv)
