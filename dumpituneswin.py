#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Copyright © 2018 David Perry
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
import win32com.client
from songparser import BaseSong, BaseLibraryParser

# Constants
ITTrackKindFile = 1

class iTunesWinSong(BaseSong):
	def __init__(self, track):
		self.track = track
		self.artist = track.Artist
		self.album = track.Album
		self.title = track.Name
		self.size = track.Size
		self.rating = track.Rating
		self.playcount = track.PlayedCount
		self.filePath = track.Location

	def setRating(self, rating):
		self.track.Rating = rating

	def setPlaycount(self, playcount):
		self.track.PlayedCount = playcount

class iTunesWinParser(BaseLibraryParser):
	def __init__(self):
		self.comInstance = win32com.client.Dispatch("iTunes.Application")
		self.library = self.comInstance.LibrarySource.Playlists.ItemByName("Library")

	def getSongs(self):
		return self.getPlaylistFiles('Library')

	def getPlaylistFiles(self, playlistName):
		playlist = self.comInstance.LibrarySource.Playlists.ItemByName(playlistName)
		if playlist:
			return [iTunesWinSong(s) for s in playlist.Tracks if s.Kind == ITTrackKindFile]
		return []

	def findSongBySize(self, size):
		return [iTunesWinSong(s) for s in self.library.Tracks if s.Kind == ITTrackKindFile and s.Size == size]

	#@abstractmethod
	def findSongByTitle(self, title):
		track = self.library.Tracks.ItemByName(title)
		if track:
			return [iTunesWinSong(track)]
		return []

	def save(self):
		pass

def main(argv):
	print "Reading from iTunes running on Windows (win32com)"
	parser = iTunesWinParser()

	if len(argv) == 2:
		print "Using playlist " + argv[1]
		allSongs = parser.getPlaylistFiles(argv[1])
	else:
		allSongs = parser.getSongs()

	for song in allSongs:
		print("{0} - {1} - {2} - {3}".format(
			song.artist.encode("ascii", "replace"),
			song.album.encode("ascii", "replace"),
			song.title.encode("ascii", "replace"),
			song.size))

if __name__ == "__main__":
	main(sys.argv)
