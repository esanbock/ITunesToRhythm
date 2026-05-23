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

# Try to import libxml2 directly, fall back to adapter if not available
try:
    import libxml2
except ImportError:
    # Use our adapter instead of libxml2
    import libxml2_adapter as libxml2
    print("Using libxml2 adapter (lxml-based) as libxml2 is not installed")

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
            dateaddedValueNode = libxml2.newNode("first-seen")
            newdateaddedKeyNode.addSibling(dateaddedValueNode)
        else:
            dateaddedValueNode = dateaddedValueNodes[0]

        dateaddedValueNode.setContent(str(dateadded))

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
