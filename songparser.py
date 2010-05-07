#!/usr/bin/env python
#
# iTunesToRhythm is free software; you can redistribute it and/or modify
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

import libxml2

class BaseSong:
	def __init__(self, song):
		self.artist = "Unknown"
		self.album = "Unknown"
		self.title = "Unknown"
		self.size = "Unknown"
		self.rating = 0
		self.playcount = 0

class BaseLibraryParser:
	def __init__(self, location):
		self.doc = libxml2.parseFile( location )
		self.xpathContext = self.doc.xpathNewContext()
		return
		
	def getSongs(self):
		return
	
	def save(self, location): 
		self.doc.saveFile( location )
