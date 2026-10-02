import time
import unittest

from dumpitunes import iTunesLibraryParser
from helpers import ITUNES_FIXTURE, TempLibraryTestCase, quiet


def loadParser(path):
    with quiet():
        return iTunesLibraryParser(path)


def songsByTitle(parser):
    return {s.title: s for s in parser.getSongs()}


class ITunesReadTest(unittest.TestCase):
    def setUp(self):
        self.songs = songsByTitle(loadParser(ITUNES_FIXTURE))

    def test_reads_all_tracks(self):
        self.assertEqual(sorted(self.songs), ["Song A", "Song B", "Twin One", "Twin Two"])

    def test_reads_fields(self):
        song = self.songs["Song A"]
        self.assertEqual(song.artist, "Artist A")
        self.assertEqual(song.album, "Album A")
        self.assertEqual(song.size, "1000001")
        self.assertEqual(song.rating, 80)
        self.assertEqual(song.playcount, 5)
        self.assertEqual(song.filePath, "file://localhost/music/song_a.mp3")
        self.assertEqual(song.dateadded, int(time.mktime(time.strptime("2010-01-15T12:00:00Z", "%Y-%m-%dT%H:%M:%SZ"))))

    def test_missing_fields_get_defaults(self):
        song = self.songs["Song B"]
        self.assertEqual(song.album, "Unknown")
        self.assertEqual(song.rating, 0)
        self.assertEqual(song.playcount, 0)
        self.assertEqual(song.filePath, "")
        self.assertEqual(song.dateadded, 0)

    def test_findSongBySize_returns_every_match(self):
        parser = loadParser(ITUNES_FIXTURE)
        matches = parser.findSongBySize("3000003")
        self.assertEqual(sorted(s.title for s in matches), ["Twin One", "Twin Two"])

    def test_findSongBySize_no_match(self):
        self.assertEqual(loadParser(ITUNES_FIXTURE).findSongBySize("42"), [])


class ITunesWriteTest(TempLibraryTestCase):
    def reload(self, parser):
        with quiet():
            parser.save()
        return songsByTitle(loadParser(self.itunesPath))

    def test_updates_existing_rating_and_playcount(self):
        parser = loadParser(self.itunesPath)
        song = songsByTitle(parser)["Song A"]
        song.setRating(20)
        song.setPlaycount(42)
        saved = self.reload(parser)["Song A"]
        self.assertEqual(saved.rating, 20)
        self.assertEqual(saved.playcount, 42)

    def test_adds_missing_rating_and_playcount(self):
        parser = loadParser(self.itunesPath)
        song = songsByTitle(parser)["Song B"]
        song.setRating(60)
        song.setPlaycount(9)
        saved = self.reload(parser)["Song B"]
        self.assertEqual(saved.rating, 60)
        self.assertEqual(saved.playcount, 9)

    def test_dateadded_round_trips(self):
        epoch = int(time.mktime((2012, 1, 20, 8, 30, 0, 0, 0, -1)))
        parser = loadParser(self.itunesPath)
        songs = songsByTitle(parser)
        songs["Song A"].setDateAdded(epoch)
        songs["Song B"].setDateAdded(epoch)
        saved = self.reload(parser)
        self.assertEqual(saved["Song A"].dateadded, epoch)
        self.assertEqual(saved["Song B"].dateadded, epoch)


if __name__ == "__main__":
    unittest.main()
