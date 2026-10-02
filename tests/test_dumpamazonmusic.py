import unittest

try:
    import dumpAmazonMusic
except ImportError:  # rleveldb is optional
    dumpAmazonMusic = None


@unittest.skipIf(dumpAmazonMusic is None, "Amazon Music support needs rleveldb")
class AmazonMusicParserTest(unittest.TestCase):
    def test_matches_by_title_only(self):
        self.assertFalse(dumpAmazonMusic.AmazonMusicParser.canMatchBySize)
        self.assertFalse(dumpAmazonMusic.AmazonMusicParser.supportsDates)

    def test_reads_track_json(self):
        song = dumpAmazonMusic.AmazonMusicSong(
            {"title": "Song", "artist": {"name": "Artist"}, "album": {"name": "Album"}, "asin": "B000"}
        )
        self.assertEqual((song.title, song.artist, song.album, song.asin), ("Song", "Artist", "Album", "B000"))


if __name__ == "__main__":
    unittest.main()
