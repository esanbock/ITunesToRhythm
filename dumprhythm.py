import sys
import libxml2
from songparser import BaseSong, BaseLibraryParser

class RhythmSong(BaseSong):
	def __init__(self, song):
		self.artist = song.xpathEval("artist")[0].content
		self.album = song.xpathEval("album")[0].content
		self.title = song.xpathEval("title")[0].content
		self.size = song.xpathEval("file-size")[0].content

def main(argv):
	location = argv[1]
	print "Reading database from " + location
	parser = RhythmLibraryParser();
        allSongs = parser.getSongs( location )
        for song in allSongs:
                print song.artist + " - " + song.album + " - " + song.title + " - " + song.size

class RhythmLibraryParser( BaseLibraryParser ):
	def getSongs(self):
		allSongNodes = xpathContext.xpathEval("//entry[@type='song']")
		allSongs = []
		for songNode in allSongNodes:
		        rhythmsong = RhythmSong( songNode )
			allSongs.append( rhythmsong )
		return allSongs
	
if __name__ == "__main__":
	main(sys.argv)
