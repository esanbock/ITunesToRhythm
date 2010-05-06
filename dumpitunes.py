import sys
import libxml2
from songparser import BaseSong, BaseLibraryParser

class iTunesSong( BaseSong ):
        def __init__(self, song):
                self.artist = song.xpathEval("string[preceding-sibling::* = 'Artist']")
                self.album = song.xpathEval("string[preceding-sibling::* = 'Album']")
                self.title = song.xpathEval("string[preceding-sibling::* = 'Name']")[0].content
                self.size = song.xpathEval("integer[preceding-sibling::* = 'Size']")
		
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

def main(argv):
        location = argv[1]
        print "Reading iTunes library from " + location
	parser = iTunesLibraryParser(location);
        allSongs = parser.getSongs( )
        for song in allSongs:
                print song.artist + " - " + song.album + " - " + song.title + " - " + song.size

class iTunesLibraryParser( BaseLibraryParser ):
	def getSongs(self):
		allSongNodes = self.xpathContext.xpathEval("/plist/dict/dict/dict/*/..")
		allSongs = []
		for songNode in allSongNodes:
		        itunesSong = iTunesSong( songNode )
			allSongs.append( itunesSong )
		return allSongs
	
	def findSongBySize( self, size ):
		matches = self.xpathContext.xpathEval("/plist/dict/dict/dict[integer = '" + str(size) + "']")
		matchingsongs = []
		for match in matches:
			song = iTunesSong( match )
			matchingsongs.insert( song )
		return matchingsongs
		
if __name__ == "__main__":
        main(sys.argv)

