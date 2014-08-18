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
import lxml
from songparser import BaseSong, BaseLibraryParser

class RhythmSong(BaseSong):
	def __init__(self, node):
		self.xmlNode = node
		self.artist = self.xmlNode.xpath("artist")[0].text
		self.album = self.xmlNode.xpath("album")[0].text
		self.title = self.xmlNode.xpath("title")[0].text
		self.size = self.xmlNode.xpath("file-size")[0].text
		self.filePath = self.xmlNode.xpath("location")[0].text
		self.playcount = self.xmlNode.xpath("play-count")
		self.rating = self.xmlNode.xpath("rating")

		if len(self.playcount) == 0:
			self.playcount = 0
		else:
			self.playcount = int(self.playcount[0].text)

		if len(self.rating) == 0:
			self.rating = 0
		else:
			self.rating = int(self.rating[0].text) * 20


	def setRating(self, rating):
		ratingNode = self.xmlNode.xpath("rating")
		if len(ratingNode) == 0:
			newNode = etree.Element("rating")
			newNode.text = str(rating / 20)
			self.xmlNode.append(newNode)
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
		allSongNodes = self.doc.xpath("//entry[@type='song']")
		return [RhythmSong(s) for s in allSongNodes]

	def findSongBySize(self, size):
		matches = self.doc.xpath("//entry[@type='song' and file-size = '" + str(size)  + "']")
		matchingsongs = []
		for match in matches:
			song = RhythmSong(match)
			matchingsongs.append(song)
		return matchingsongs

if __name__ == "__main__":
	main(sys.argv)
