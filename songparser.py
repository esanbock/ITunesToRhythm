#!/usr/bin/env python
#
# Copyright @ 2010 Douglas Esanbock
# Modifications to import "Date Added" Copyright @ September 2013 Edgar Salgado
# iTunesToRhythm is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# iTunesToRhythm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with iTunesToRhythm; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA


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
        self.playdate = 0


class BaseLibraryParser(object):
    # whether songs carry real file sizes to match on
    canMatchBySize = True
    # whether songs can read and write "date added" and "last played"
    supportsDates = False

    def __init__(self, location):
        # Imported here rather than at module level so backends that never
        # parse an XML file (e.g. iTunes on macOS) can use these base classes
        # without an XML library installed. Try the native libxml2 bindings,
        # falling back to the lxml-based adapter; any failure from the adapter
        # (e.g. lxml also missing) propagates to the caller.
        try:
            import libxml2
        except ImportError:
            import libxml2_adapter as libxml2

        print("Loading file " + location)
        self.location = location
        self.doc = libxml2.parseFile(location)
        self.xpathContext = self.doc.xpathNewContext()
        print("File loaded")

    # @abstractmethod
    def getSongs(self):
        raise NotImplementedError("Must override this method in a subclass")

    # @abstractmethod
    def findSongBySize(self, size):
        results = []
        allSongs = self.getSongs()
        for song in allSongs:
            if song.size == size:
                results.append(song)
                return results

    # @abstractmethod
    def findSongByTitle(self, title):
        results = []
        allSongs = self.getSongs()
        for song in allSongs:
            if song.title == title:
                results.append(song)
                return results

    # @abstractmethod
    def save(self):
        self.doc.saveFile(self.location)
