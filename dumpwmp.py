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
import win32com.client
from songparser import BaseSong, BaseLibraryParser

class WMPSong(BaseSong):
        def __init__(self, WMPSong):
                self.wmpNode = WMPSong
                self.artist = WMPSong.getItemInfo("Author")
                self.album = WMPSong.getItemInfo("WM/AlbumTitle")
                self.title = WMPSong.name
                self.size = WMPSong.getItemInfo("FileSize")
                self.rating = WMPSong.getItemInfo("UserRating")
                self.playcount = WMPSong.getItemInfo("UserPlaycount")
                self.filePath = WMPSong.sourceURL

        def setRating(self, rating):
                self.wmpNode.setItemInfo("UserRating", rating)

        def setPlaycount(self, playcount):
                self.wmpNode.setItemInfo("UserPlaycount", rating)

class WMPParser(BaseLibraryParser):
        def __init__(self):
                self.wmp = win32com.client.Dispatch("WMPlayer.OCX");

        def getSongs(self):
                songs = self.wmp.mediaCollection.getAll()
                result = []
                for s in songs:
                        wmpSong = WMPSong(s)
                        result.append(s)
                        print wmpSong.filePath
                return result;

        def save(self):
                pass

def main(argv):
        print "Reading from Windows Media Player"
        parser = WMPParser()

        allSongs = parser.getSongs()

        for song in allSongs:
                print song.artist + " - " + song.album + " - " + song.title + " - " + str(song.size)

if __name__ == "__main__":
        main(sys.argv)