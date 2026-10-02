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

import calendar
import sys
import time
import os

# Try to import the native libxml2 bindings, falling back to the lxml-based
# adapter when they are unavailable. When imported by iTunesToRhythm.py a
# missing backend propagates to the caller; only a direct script run turns it
# into a friendly message and exit.
try:
    import libxml2
except ImportError:
    try:
        import libxml2_adapter as libxml2
    except ImportError as exc:
        # When imported as a library (by iTunesToRhythm.py), re-raise so the
        # caller handles the missing backend. When run directly as a script,
        # print a friendly message and exit instead of dumping a traceback.
        if __name__ == "__main__":
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        raise

from songparser import BaseSong, BaseLibraryParser


class iTunesSong(BaseSong):
    def __init__(self, songNode):
        self.xmlNode = songNode
        self.artist = self.xmlNode.xpathEval("string[preceding-sibling::* = 'Artist']")
        self.album = self.xmlNode.xpathEval("string[preceding-sibling::* = 'Album']")
        self.title = self.xmlNode.xpathEval("string[preceding-sibling::* = 'Name']")[0].content
        self.size = self.xmlNode.xpathEval("integer[preceding-sibling::* = 'Size']")
        self.rating = self.xmlNode.xpathEval("integer[preceding-sibling::* = 'Rating']")
        self.playcount = self.xmlNode.xpathEval("integer[preceding-sibling::* = 'Play Count']")
        try:
            self.filePath = self.xmlNode.xpathEval("string[preceding-sibling::* = 'Location']")[0].content
        except IndexError:
            self.filePath = ""
        self.dateadded = self.xmlNode.xpathEval("date[preceding-sibling::* = 'Date Added']")
        self.playdate = self.xmlNode.xpathEval("date[preceding-sibling::* = 'Play Date UTC']")

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

        if len(self.dateadded) == 0:
            self.dateadded = 0
        else:
            # 'Date Added' is UTC, so convert with timegm to a Unix epoch
            self.dateadded = calendar.timegm(time.strptime(self.dateadded[0].content, "%Y-%m-%dT%H:%M:%SZ"))

        if len(self.playdate) == 0:
            self.playdate = 0
        else:
            # 'Play Date UTC' is UTC, so convert with timegm to a Unix epoch
            self.playdate = calendar.timegm(time.strptime(self.playdate[0].content, "%Y-%m-%dT%H:%M:%SZ"))

    def setRating(self, rating):
        ratingValueNodes = self.xmlNode.xpathEval("integer[preceding-sibling::* = 'Rating'][1]")
        if len(ratingValueNodes) == 0:
            newRatingKeyNode = libxml2.newNode("key")
            self.xmlNode.addChild(newRatingKeyNode)
            newRatingKeyNode.setContent("Rating")
            ratingValueNode = libxml2.newNode("integer")
            newRatingKeyNode.addSibling(ratingValueNode)
        else:
            ratingValueNode = ratingValueNodes[0]

        ratingValueNode.setContent(str(rating))

    def setPlaycount(self, playcount):
        playcountValueNodes = self.xmlNode.xpathEval("integer[preceding-sibling::* = 'Play Count'][1]")
        if len(playcountValueNodes) == 0:
            newPlaycountKeyNode = libxml2.newNode("key")
            self.xmlNode.addChild(newPlaycountKeyNode)
            newPlaycountKeyNode.setContent("Play Count")
            playcountValueNode = libxml2.newNode("integer")
            newPlaycountKeyNode.addSibling(playcountValueNode)
        else:
            playcountValueNode = playcountValueNodes[0]

        playcountValueNode.setContent(str(playcount))

    def setDateAdded(self, dateadded):
        dateaddedValueNodes = self.xmlNode.xpathEval("date[preceding-sibling::* = 'Date Added'][1]")
        if len(dateaddedValueNodes) == 0:
            newdateaddedKeyNode = libxml2.newNode("key")
            self.xmlNode.addChild(newdateaddedKeyNode)
            newdateaddedKeyNode.setContent("Date Added")
            # The value element must be <date> so it matches the key xpath above
            # and the ISO-8601 format the constructor parses on read.
            dateaddedValueNode = libxml2.newNode("date")
            newdateaddedKeyNode.addSibling(dateaddedValueNode)
        else:
            dateaddedValueNode = dateaddedValueNodes[0]

        # dateadded is a Unix epoch; iTunes stores it as an ISO-8601 UTC date
        dateaddedValueNode.setContent(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(dateadded))))

    def setPlayDate(self, playdate):
        playdateValueNodes = self.xmlNode.xpathEval("date[preceding-sibling::* = 'Play Date UTC'][1]")
        if len(playdateValueNodes) == 0:
            newPlaydateKeyNode = libxml2.newNode("key")
            self.xmlNode.addChild(newPlaydateKeyNode)
            newPlaydateKeyNode.setContent("Play Date UTC")
            playdateValueNode = libxml2.newNode("date")
            newPlaydateKeyNode.addSibling(playdateValueNode)
        else:
            playdateValueNode = playdateValueNodes[0]

        # playdate is a Unix epoch; iTunes stores it as an ISO-8601 UTC date
        playdateValueNode.setContent(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(playdate))))


class iTunesLibraryParser(BaseLibraryParser):
    supportsDates = True

    def getSongs(self):
        allSongNodes = self.xpathContext.xpathEval("/plist/dict/dict/dict/*/..")
        return [iTunesSong(s) for s in allSongNodes]

    def findSongBySize(self, size):
        # Index track nodes by their 'Size' value once, so lookups compare only
        # the file size (not every integer in the track) without rescanning the
        # library. Songs are rebuilt from the nodes on each call so they always
        # reflect the current XML.
        if not hasattr(self, "_nodesBySize"):
            self._nodesBySize = {}
            for node in self.xpathContext.xpathEval("/plist/dict/dict/dict/*/.."):
                self._nodesBySize.setdefault(iTunesSong(node).size, []).append(node)
        return [iTunesSong(node) for node in self._nodesBySize.get(str(size), [])]


def main(argv):
    if len(argv) < 2:
        # Try to find iTunes Music Library.xml in the default location
        home_dir = os.path.expanduser("~")
        default_path = os.path.join(home_dir, "Music", "iTunes", "iTunes Music Library.xml")

        if os.path.exists(default_path):
            location = default_path
            print(f"Using default iTunes library at {location}")
        else:
            print("Usage: python3 dumpitunes.py <path_to_iTunes_Library.xml>")
            print("Example: python3 dumpitunes.py ~/Music/iTunes/iTunes Music Library.xml")
            print(f"Default library not found at {default_path}")
            return
    else:
        location = argv[1]

    # Check if file exists
    if not os.path.exists(location):
        print(f"Error: File '{location}' does not exist.")
        return

    print("Reading iTunes library from " + location)
    parser = iTunesLibraryParser(location)
    allSongs = parser.getSongs()
    print(f"Found {len(allSongs)} songs")

    # Print all songs
    for i, song in enumerate(allSongs):
        print(f"{i+1}. {song.artist} - {song.album} - {song.title} - {song.size}")


if __name__ == "__main__":
    main(sys.argv)
