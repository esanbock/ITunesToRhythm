import unittest

from dumprhythm import RhythmLibraryParser
from helpers import RHYTHM_FIXTURE, TempLibraryTestCase, quiet


def loadParser(path):
    with quiet():
        return RhythmLibraryParser(path)


def songsByTitle(parser):
    return {s.title: s for s in parser.getSongs()}


class RhythmReadTest(unittest.TestCase):
    def setUp(self):
        self.songs = songsByTitle(loadParser(RHYTHM_FIXTURE))

    def test_reads_only_songs(self):
        self.assertEqual(sorted(self.songs), ["Orphan", "Song A", "Song B", "Twin Two"])

    def test_reads_fields(self):
        song = self.songs["Song A"]
        self.assertEqual(song.artist, "Artist A")
        self.assertEqual(song.album, "Album A")
        self.assertEqual(song.size, "1000001")
        self.assertEqual(song.filePath, "file:///music/song_a.mp3")
        self.assertEqual(song.playcount, 1)
        self.assertEqual(song.dateadded, 1275110148)
        self.assertEqual(song.playdate, 1301792996)

    def test_rating_is_scaled_from_stars_to_100(self):
        self.assertEqual(self.songs["Song A"].rating, 40)

    def test_missing_fields_get_defaults(self):
        song = self.songs["Song B"]
        self.assertEqual(song.rating, 0)
        self.assertEqual(song.playcount, 0)
        self.assertEqual(song.playdate, 0)

    def test_findSongBySize(self):
        parser = loadParser(RHYTHM_FIXTURE)
        self.assertEqual([s.title for s in parser.findSongBySize("2000002")], ["Song B"])
        self.assertEqual(parser.findSongBySize("42"), [])


class RhythmWriteTest(TempLibraryTestCase):
    def reload(self, parser):
        with quiet():
            parser.save()
        return songsByTitle(loadParser(self.rhythmPath))

    def test_updates_existing_fields(self):
        parser = loadParser(self.rhythmPath)
        song = songsByTitle(parser)["Song A"]
        song.setRating(80)
        song.setPlaycount(12)
        song.setDateAdded(1300000000)
        song.setPlayDate(1400000000)
        saved = self.reload(parser)["Song A"]
        self.assertEqual(saved.rating, 80)
        self.assertEqual(saved.playcount, 12)
        self.assertEqual(saved.dateadded, 1300000000)
        self.assertEqual(saved.playdate, 1400000000)

    def test_adds_missing_fields(self):
        parser = loadParser(self.rhythmPath)
        song = songsByTitle(parser)["Song B"]
        song.setRating(100)
        song.setPlaycount(3)
        song.setPlayDate(1400000000)
        saved = self.reload(parser)["Song B"]
        self.assertEqual(saved.rating, 100)
        self.assertEqual(saved.playcount, 3)
        self.assertEqual(saved.playdate, 1400000000)


if __name__ == "__main__":
    unittest.main()
