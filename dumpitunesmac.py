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
from appscript import *
from songparser import BaseSong, BaseLibraryParser

class iTunesMacSong(BaseSong):
	def __init__(self, iTunesNode):
		self.iTunesNode = iTunesNode
		self.artist = self.iTunesNode.artist()
		self.album = self.iTunesNode.album()
		self.title = self.iTunesNode.name()
		self.size = self.iTunesNode.size()
		self.rating = self.iTunesNode.rating()
		self.playcount = self.iTunesNode.played_count()
		self.filePath = self.iTunesNode.location().path

	def setRating(self, rating):
		self.iTunesNode.rating.set(rating)

	def setPlaycount(self, playcount):
		self.iTunesNode.played_count.set(playcount)

class iTunesMacParser(BaseLibraryParser):
	def __init__(self):
		self.iTunes = app('iTunes')

	def getSongs(self):
		return self.getPlaylistFiles('Library')

	def getPlaylistFiles(self, playlistName):
		library = self.iTunes.library_playlists[playlistName]
		return [iTunesMacSong(s) for s in library.file_tracks()]

	def save(self):
		pass

def main(argv):
	print "Reading from iTunes running on Mac (appscript)"
	parser = iTunesMacParser()

	if len(argv) == 2:
		print "Using playlist " + argv[1]
		allSongs = parser.getPlaylistFiles(argv[1])
	else:
		allSongs = parser.getSongs()

	for song in allSongs:
		print song.artist + " - " + song.album + " - " + song.title + " - " + str(song.size)

if __name__ == "__main__":
	main(sys.argv)
