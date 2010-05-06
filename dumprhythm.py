import sys
import libxml2
from songparser import BaseSong, BaseLibraryParser

class RhythmSong(BaseSong):
	def __init__(self, node):
		self.xmlNode = node
		self.artist = self.xmlNode.xpathEval("artist")[0].content
		self.album = self.xmlNode.xpathEval("album")[0].content
		self.title = self.xmlNode.xpathEval("title")[0].content
		self.size = self.xmlNode.xpathEval("file-size")[0].content
	
	def setRating( self, rating ):
		self.xmlNode.xpathEval("rating")[0].setContent( str(rating) )

def main(argv):
	location = argv[1]
	print "Reading database from " + location
	parser = RhythmLibraryParser( location );
        allSongs = parser.getSongs()
        for song in allSongs:
                print song.artist + " - " + song.album + " - " + song.title + " - " + song.size

class RhythmLibraryParser( BaseLibraryParser ):
	def getSongs(self):
		allSongNodes = self.xpathContext.xpathEval("//entry[@type='song']")
		allSongs = []
		for songNode in allSongNodes:
		        rhythmsong = RhythmSong( songNode )
			allSongs.append( rhythmsong )
		return allSongs
	
if __name__ == "__main__":
	main(sys.argv)
