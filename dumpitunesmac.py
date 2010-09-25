#!/usr/bin/env python2.3
#
#  dumpItunesMac.py
#  
#
#  Created by esanbockd on 5/28/10.
#  Copyright (c) 2010 __MyCompanyName__. All rights reserved.
#
import sys
import platform
if platform.system() == "Darwin":
	sys.path.append('/sw/lib/python2.5/site-packages/')
from appscript import *
from songparser import BaseSong, BaseLibraryParser
	
class iTunesMacSong( BaseSong ):
	def __init__(self, iTunesNode ):
		self.iTunesNode = iTunesNode
		self.artist = self.iTunesNode.artist()
		self.album = self.iTunesNode.album()
		self.title = self.iTunesNode.name()
		self.size = self.iTunesNode.size()
		self.rating = self.iTunesNode.rating()
		self.playcount = self.iTunesNode.played_count()
		self.filePath = self.iTunesNode.location().path
		
	def setRating( self, rating ):
		self.iTunesNode.rating.set(rating)
		
	def setPlaycount( self, playcount ):
		self.iTunesNode.played_count.set( playcount )

class iTunesMacParser( BaseLibraryParser ):
	def __init__(self):
			self.iTunes = app('iTunes')
			
	def getSongs(self):
		return getPlaylistFiles('Library')
		
	def getPlaylistFiles( self, playlistName ):
		self.library = self.iTunes.library_playlists[playlistName]
		results=[]
		allSongs = self.library.file_tracks()
		for song in allSongs:
			iTunesSong = iTunesMacSong( song )
			results.append(iTunesSong)
		return results
		
	def save(self):
		return

def main( argv ):
	print "Reading from iTunes running on Mac (appscript)"
	parser = iTunesMacParser()
	
	if len(argv) == 2:
		print "Using playlist " + argv[1]
		allSongs = parser.getPlaylistFiles( argv[1] )
	else:
		allSongs = parser.getSongs()
		
	for song in allSongs:
		print song.artist + " - " + song.album + " - " + song.title + " - " + str(song.size)
				
if __name__ == "__main__":
        main(sys.argv)
