class BaseSong:
        def __init__(self, song):
                self.artist = "Unknown"
                self.album = "Unknown"
                self.title = "Unknown"
                self.size = "Unknown"

class BaseLibraryParser:
	def __init__(self, location):
		self.doc = libxml2.parseFile( location )
		self.xpathContext = doc.xpathNewContext()
		return
		
	def getSongs(self):
		return
