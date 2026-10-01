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
        #http://www.epochconverter.com/
            self.dateadded = int(time.mktime(time.strptime(self.dateadded[0].content, '%Y-%m-%dT%H:%M:%SZ')))


    def setRating(self,  rating):
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

        # The constructor stores dateadded as an epoch int (via time.mktime).
        # Write it back in the same ISO-8601 form iTunes uses so a later read
        # round-trips through time.strptime('%Y-%m-%dT%H:%M:%SZ') correctly.
        isoDate = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(int(dateadded)))
        dateaddedValueNode.setContent(isoDate)

class iTunesLibraryParser(BaseLibraryParser):
    def getSongs(self):
        allSongNodes = self.xpathContext.xpathEval("/plist/dict/dict/dict/*/..")
        return [iTunesSong(s) for s in allSongNodes]

    def findSongBySize(self, size):
        matches = self.xpathContext.xpathEval("/plist/dict/dict/dict[integer = '" + str(size) + "']")
        matchingsongs = []
        for match in matches:
            song = iTunesSong(match)
            matchingsongs.append(song)
        return matchingsongs

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
