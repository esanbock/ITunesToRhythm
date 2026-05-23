#!/usr/bin/env python
#
#Copyright @ 2024 Douglas Esanbock
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
import os
import json
import re
import rleveldb
from songparser import BaseSong

DEFAULT_DB_PATH = os.path.join(
	os.environ.get("LOCALAPPDATA", ""),
	"Packages", "AmazonMobileLLC.AmazonMusic_kc6t79cpj4tp0",
	"LocalCache", "Local", "Amazon Music", "Data", "Local Storage"
)

class AmazonMusicSong(BaseSong):
	def __init__(self, track_json):
		self.title = track_json.get("title", "Unknown")
		self.artist = track_json.get("artist", {}).get("name", "Unknown")
		album = track_json.get("album", {})
		self.album = album.get("name", album.get("title", "Unknown"))
		self.asin = track_json.get("asin", "")
		self.duration = track_json.get("duration", "0")
		self.trackNumber = track_json.get("trackNumber", "0")
		self.size = "0"
		self.rating = 0
		self.playcount = 0
		self.filePath = ""
		self.dateadded = 0
		self.playdate = 0

class AmazonMusicParser:
	def __init__(self, db_path=None):
		self.db_path = db_path or DEFAULT_DB_PATH
		if not os.path.isdir(self.db_path):
			raise FileNotFoundError(f"Amazon Music database not found at: {self.db_path}")
		print(f"Reading Amazon Music library from {self.db_path}")

	def getSongs(self):
		songs = []
		seen_ids = set()
		seen_artist_title = set()
		db = rleveldb.RawLevelDb(self.db_path)
		for rec in db.iterate_records_raw():
			key = rec.user_key.decode('utf-8', errors='replace')
			# Read from all MusicContent CacheEntry keys that may contain tracks
			if '.MusicContent.CacheEntry.' not in key:
				continue
			val = rec.value
			text = val.decode('utf-8', errors='replace')
			json_start = text.find('{')
			if json_start < 0:
				continue
			# Find the end of the JSON object by matching braces
			json_str = self._extract_json(text[json_start:])
			if json_str:
				try:
					data = json.loads(json_str)
					if isinstance(data, dict) and data.get("type") == "track":
						# Deduplicate by track id or asin
						track_id = data.get("id") or data.get("asin") or ""
						if track_id and track_id in seen_ids:
							continue
						if track_id:
							seen_ids.add(track_id)
						# Also deduplicate by artist+title for entries without IDs
						artist = data.get("artist", {}).get("name", "")
						title = data.get("title", "")
						artist_title_key = (artist.lower(), title.lower())
						if not track_id:
							if artist_title_key in seen_artist_title:
								continue
						seen_artist_title.add(artist_title_key)
						songs.append(AmazonMusicSong(data))
				except json.JSONDecodeError:
					pass
		db.close()
		return songs

	def _extract_json(self, text):
		depth = 0
		for i, ch in enumerate(text):
			if ch == '{':
				depth += 1
			elif ch == '}':
				depth -= 1
				if depth == 0:
					return text[:i+1]
		return None

	def findSongByTitle(self, title):
		return [s for s in self.getSongs() if s.title == title]

	def save(self):
		pass

def main(argv):
	import io
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
	db_path = argv[1] if len(argv) > 1 else None
	parser = AmazonMusicParser(db_path)
	allSongs = parser.getSongs()
	print(f"\nFound {len(allSongs)} tracks:\n")
	for song in allSongs:
		print(f"{song.artist} - {song.album} - {song.title} ({song.duration}s)")

if __name__ == "__main__":
	main(sys.argv)
