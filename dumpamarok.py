import sys
import MySQLdb
from songparser import BaseSong, BaseLibraryParser


def main(argv):
	server =argv[1]
	database = argv[2]
	username = argv[3]
	pwd = argv[4]
	
	print "Reading database from " + username + "@" + server + "/" + database
	parser = AmarokLibraryParser( server,  database,  username,  pwd );
        allSongs = parser.getSongs()
        for song in allSongs:
                print song.artist + " - " + song.album + " - " + song.title + " - " + str(song.size)


class AmarokSong(BaseSong):
	def __init__(self, database,  row):
		self.db = database
		self.id = int(row[0])
		self.artist =row[1]
		self.title  = row[2]
		self.album= row[3]
		self.size = row[4]
		self.filePath = row[5]
		self.playcount = row[6]
		if self.playcount == None:
			self.playcount = 0
		
		if row[7] == None:
			self.rating = 0
		else:
			self.rating = row[7] * 10

	def getStatUrlId( self):
		cursor = self.db.cursor()
		cursor.execute("select statistics.id as statid, urls.id as urlid from urls " +
									"inner join tracks on tracks.url = urls.id " +
									"left outer join statistics on urls.id = statistics.url " +
									"where tracks.id=%d" % (self.id ) )
		result = cursor.fetchone()
		return result[0],result[1]
		
	
	def setRating( self, rating ):
		statid, urlid = self.getStatUrlId()
		cursor = self.db.cursor()
		if  statid != None:
			# run an update
			cursor.execute("update statistics set rating = %d where id = %d " %  (rating / 10,  statid))
		else:
			# run an insert
			cursor.execute("insert into statistics (url,rating) values (%d,%d)" % (urlid,  rating / 10))
	   
	def setPlaycount( self, playcount ):
		statid, urlid = self.getStatUrlId()
		cursor = self.db.cursor()
		if  statid != None:
			# run an update
			cursor.execute("update statistics set playcount = %d where id = %d " %  (playcount,  statid))
		else:
			# run an insert
			cursor.execute("insert into statistics (url,playcount) values (%d,%d)" % (urlid,  playcount))

		

class AmarokLibraryParser( BaseLibraryParser ):
	def __init__(self, server,  database,  username,  pwd):
		self.db = MySQLdb.connect( host=server, db=database, user=username, passwd=pwd)
		self.querystring = "select tracks.id, artists.name, tracks.title, albums.name, tracks.filesize, urls.rpath, statistics.playcount, statistics.rating from tracks inner join artists on artists.id = tracks.artist inner join albums on albums.id = tracks.album inner join urls on urls.id = tracks.url left outer join statistics on urls.id = statistics.url  "
	
	def getSongs(self):
		cursor = self.db.cursor()
		query = cursor.execute( self.querystring )
		results = cursor.fetchall()
		return self.rowsToSongs( results )
	
	def findSongBySize(self,  size):
		cursor = self.db.cursor()
		query = cursor.execute( self.querystring + " where tracks.filesize = " + size )
		results = cursor.fetchall()
		return self.rowsToSongs( results )

	def rowsToSongs(self,  results):
		allSongs = []
		for row in results:
				amarokSong = AmarokSong(self.db,  row)
				allSongs.append( amarokSong )
		return allSongs
		
	def save(self): 
		self.db.commit()
		
if __name__ == "__main__":
        main(sys.argv)

