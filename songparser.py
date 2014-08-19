#!/usr/bin/env python
#
#Copyright @ 2010 Douglas Esanbock
#Modifications to import "Date Added" Copyright @ September 2013 Edgar Salgado
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
import libxml2

class BaseSong(object):
	def __init__(self, song):
		self.artist = "Unknown"
		self.album = "Unknown"
		self.title = "Unknown"
		self.size = "Unknown"
		self.rating = 0
		self.playcount = 0
		self.filePath = ""
		self.dateadded = 0

class BaseLibraryParser(object):
	def __init__(self, location):
		print( "loading file " + location );
		self.location = location
		self.doc = libxml2.parseFile(location)
		self.xpathContext = self.doc.xpathNewContext()
		print( "file loaded " );

	#@abstractmethod
	def getSongs(self):
		raise NotImplementedError("Must override this method in a subclass")

	#@abstractmethod
	def findSongBySize(self, size):
		results = []
		allSongs = self.getSongs()
		for song in allSongs:
			if song.size == size:
				results.append(song)
				return results
				
	#@abstractmethod
	def save(self):
		self.doc.saveFile(self.location)
