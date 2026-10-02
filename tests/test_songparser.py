import unittest

from songparser import BaseSong, BaseLibraryParser


def makeSong(title, size):
    song = BaseSong(None)
    song.title = title
    song.size = size
    return song


class StubParser(BaseLibraryParser):
    def __init__(self, songs):
        self.songs = songs

    def getSongs(self):
        return self.songs


class BaseSongTest(unittest.TestCase):
    def test_defaults(self):
        song = BaseSong(None)
        self.assertEqual(song.artist, "Unknown")
        self.assertEqual(song.album, "Unknown")
        self.assertEqual(song.title, "Unknown")
        self.assertEqual(song.size, "Unknown")
        self.assertEqual(song.rating, 0)
        self.assertEqual(song.playcount, 0)
        self.assertEqual(song.filePath, "")
        self.assertEqual(song.dateadded, 0)


class BaseLibraryParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = StubParser([makeSong("One", "100"), makeSong("Two", "200"), makeSong("Three", "300")])

    def test_getSongs_must_be_overridden(self):
        parser = BaseLibraryParser.__new__(BaseLibraryParser)
        with self.assertRaises(NotImplementedError):
            parser.getSongs()

    def test_findSongBySize_single_match(self):
        matches = self.parser.findSongBySize("200")
        self.assertEqual([s.title for s in matches], ["Two"])

    def test_findSongBySize_no_match(self):
        self.assertFalse(self.parser.findSongBySize("999"))

    def test_findSongByTitle_single_match(self):
        matches = self.parser.findSongByTitle("Three")
        self.assertEqual([s.size for s in matches], ["300"])

    def test_findSongByTitle_no_match(self):
        self.assertFalse(self.parser.findSongByTitle("Missing"))

    @unittest.expectedFailure
    def test_findSongBySize_returns_all_matches(self):
        # Known bug: the base implementation returns after the first match,
        # so ambiguous matches are never reported for parsers that use it
        parser = StubParser([makeSong("One", "100"), makeSong("Uno", "100")])
        self.assertEqual(len(parser.findSongBySize("100")), 2)


if __name__ == "__main__":
    unittest.main()
