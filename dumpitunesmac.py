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
import platform
import os

# Define our own BaseSong and BaseLibraryParser classes to avoid libxml2 dependency
class BaseSong(object):
    def __init__(self, song):
        self.artist = "Unknown"
        self.album = "Unknown"
        self.title = "Unknown"
        self.size = "Unknown"
        self.rating = 0
        self.playcount = 0
        self.filePath = ""
        self.dateadded = 0

class BaseLibraryParser(object):
    def __init__(self, location):
        self.location = location

    def getSongs(self):
        raise NotImplementedError("Must override this method in a subclass")

    def findSongBySize(self, size):
        results = []
        allSongs = self.getSongs()
        for song in allSongs:
            if song.size == size:
                results.append(song)
                return results

    def findSongByTitle(self, title):
        results = []
        allSongs = self.getSongs()
        for song in allSongs:
            if song.title == title:
                results.append(song)
                return results

    def save(self):
        pass

# Check if we're on macOS
if platform.system() == "Darwin":
    # Import ScriptingBridge directly without Foundation
    import ScriptingBridge

class iTunesMacSong(BaseSong):
    def __init__(self, track):
        super().__init__(None)
        self.track = track
        
        try:
            self.artist = track.artist() or "Unknown"
        except:
            self.artist = "Unknown"
            
        try:
            self.album = track.album() or "Unknown"
        except:
            self.album = "Unknown"
            
        try:
            self.title = track.name() or "Unknown"
        except:
            self.title = "Unknown"
            
        try:
            self.size = track.size()
        except:
            self.size = 0
            
        try:
            self.rating = track.rating()
        except:
            self.rating = 0
            
        try:
            self.playcount = track.playedCount()
        except:
            self.playcount = 0
        
        # Get file path
        try:
            url = track.location()
            if url:
                self.filePath = url.path()
            else:
                self.filePath = ""
        except:
            self.filePath = ""

    def setRating(self, rating):
        try:
            self.track.setRating_(rating)
        except:
            pass

    def setPlaycount(self, playcount):
        try:
            self.track.setPlayedCount_(playcount)
        except:
            pass

class iTunesMacParser(BaseLibraryParser):
    def __init__(self, location=None):
        super().__init__(location)
        
        # Determine which app to use (iTunes or Music)
        self.app_name = "Music"
        if int(platform.mac_ver()[0].split('.')[0]) < 10 or \
           (int(platform.mac_ver()[0].split('.')[0]) == 10 and int(platform.mac_ver()[0].split('.')[1]) < 15):
            self.app_name = "iTunes"
            
        # Initialize the ScriptingBridge connection
        self.music_app = ScriptingBridge.SBApplication.applicationWithBundleIdentifier_(
            f"com.apple.{self.app_name.lower()}")

    def getSongs(self):
        try:
            # Make sure the Music/iTunes app is running
            self.music_app.activate()
            
            # Get all sources
            sources = self.music_app.sources()
            if not sources or len(sources) == 0:
                print("No sources found in Music app")
                return []
            
            # Get the library source (usually the first one)
            library = sources[0]
            
            # Try a more direct approach - get all file tracks from the application
            print("Getting all file tracks directly...")
            songs = []
            
            # Get all tracks from the application
            try:
                # Try to get all tracks from the application
                all_tracks = self.music_app.tracks()
                
                # Process each track
                for track in all_tracks:
                    try:
                        # Try to create a song object for each track
                        # Don't filter by kind, just try to get all tracks
                        songs.append(iTunesMacSong(track))
                    except Exception as e:
                        print(f"Error processing track: {e}")
                        continue
            except Exception as e:
                print(f"Error getting tracks: {e}")
            
            return songs
            
        except Exception as e:
            print(f"Error getting all tracks: {e}")
            return []

    def getPlaylistFiles(self, playlistName):
        # This method is kept for compatibility but not used anymore
        return []

def main(argv):
    print(f"Reading from {'iTunes' if platform.mac_ver()[0].split('.')[0] < '10.15' else 'Music'} running on Mac (ScriptingBridge)")
    
    try:
        parser = iTunesMacParser(None)
        
        # Always use getSongs() to read all songs without processing playlists
        allSongs = parser.getSongs()

        print(f"Found {len(allSongs)} songs")
        for song in allSongs:
            print(f"{song.artist} - {song.album} - {song.title} - {song.size}")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have granted automation permissions to your terminal/IDE application.")
        print("Go to System Preferences > Security & Privacy > Privacy > Automation and enable access.")

if __name__ == "__main__":
    main(sys.argv)
