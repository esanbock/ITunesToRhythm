#!/usr/bin/env python
#
# Copyright @ 2010 Douglas Esanbock
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

import sys
import win32com.client
import win32console
import codecs
from pywintypes import com_error
from songparser import BaseSong, BaseLibraryParser

# WMP ratings use the same 0-100 scale as the rest of the program, except that
# WMP's maximum is 99, so a 5-star rating of 100 must be written as 99
WMP_MAX_RATING = 99


def wmpRatingToStandard(wmpRating):
    return 100 if wmpRating >= WMP_MAX_RATING else wmpRating


def standardRatingToWmp(rating):
    return min(rating, WMP_MAX_RATING)


class WMPSong(BaseSong):
    def __init__(self, WMPSong):
        self.wmpNode = WMPSong
        self.artist = WMPSong.getItemInfo("WM/AlbumArtist")
        self.album = WMPSong.getItemInfo("WM/AlbumTitle")
        self.title = WMPSong.name
        self.size = WMPSong.getItemInfo("FileSize")
        try:
            self.rating = wmpRatingToStandard(int(WMPSong.getItemInfo("UserRating")))
        except ValueError:
            print(WMPSong.getItemInfo("UserRating"))
            self.rating = 0
        try:
            self.playcount = int(WMPSong.getItemInfo("PlayCount"))
        except ValueError:
            print("WARNING - No playcount")
            self.playcount = 0
        self.filePath = WMPSong.sourceURL

    def setRating(self, rating):
        self.wmpNode.setItemInfo("UserRating", standardRatingToWmp(rating))

    def setPlaycount(self, playcount):
        self.wmpNode.setItemInfo("UserPlayCount", playcount)


class WMPParser(BaseLibraryParser):
    def __init__(self):
        print("initializing wmp...")
        self.wmp = win32com.client.Dispatch("WMPlayer.OCX")
        self.cachedSongs = None

    def getSongs(self):
        if self.cachedSongs is not None:
            return self.cachedSongs
        print("retrieving all songs from wmp...")
        # only audio: getAll() also returns playlists, pictures and video
        songs = self.wmp.mediaCollection.getByAttribute("MediaType", "audio")
        result = []
        try:
            # index explicitly; iterating the COM collection runs past its end
            for i in range(songs.count):
                result.append(WMPSong(songs.Item(i)))
        except com_error as badio:
            print("\t parsing stopped due to error with " + str(len(result)) + " songs")
        self.cachedSongs = result
        return result

    def save(self):
        pass

    def InitConsole(self):
        print("windows console")
        # if sys.stdout.encoding != 'cp850':
        # sys.stdout = codecs.getwriter('cp850')(sys.stdout, 'strict')


def main(argv):
    print("Reading from Windows Media Player")
    parser = WMPParser()

    allSongs = parser.getSongs()

    for song in allSongs:
        try:
            print(
                song.artist
                + " - "
                + song.album
                + " - "
                + song.title
                + " - "
                + str(song.size)
                + ", "
                + str(song.playcount)
            )
        except:
            print("\tunable to print song name")


if __name__ == "__main__":
    main(sys.argv)
