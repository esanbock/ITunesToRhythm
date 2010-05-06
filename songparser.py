import libxml2

class BaseSong:
        def __init__(self, song):
                self.artist = "Unknown"
                self.album = "Unknown"
                self.title = "Unknown"
                self.size = "Unknown"
				self.rating = 0;

class BaseLibraryParser:
	def __init__(self, location):
		self.doc = libxml2.parseFile( location )
		self.xpathContext = self.doc.xpathNewContext()
		return
		
	def getSongs(self):
		return
