import unittest
from unittest import mock

from helpers import quiet

try:
    import dumpwmp
except ImportError:  # pywin32 is only available on Windows
    dumpwmp = None


class FakeMedia:
    def __init__(self, name, size, rating, playcount):
        self.name = name
        self.sourceURL = "C:\\music\\" + name + ".mp3"
        self.info = {
            "WM/AlbumArtist": "Artist",
            "WM/AlbumTitle": "Album",
            "FileSize": size,
            "UserRating": rating,
            "PlayCount": playcount,
        }
        self.written = {}

    def getItemInfo(self, attribute):
        return self.info.get(attribute, "")

    def setItemInfo(self, attribute, value):
        self.written[attribute] = value


class FakePlaylist:
    def __init__(self, items):
        self.items = items
        self.count = len(items)

    def Item(self, index):
        return self.items[index]


class FakeMediaCollection:
    def __init__(self, audio):
        self.audio = audio

    def getByAttribute(self, attribute, value):
        if (attribute, value) != ("MediaType", "audio"):
            raise AssertionError("unexpected query")
        return FakePlaylist(self.audio)

    def getAll(self):
        raise AssertionError("getAll() includes playlists, pictures and video")


@unittest.skipIf(dumpwmp is None, "Windows Media Player support needs pywin32")
class WMPRatingTest(unittest.TestCase):
    def test_reads_ratings_unchanged_except_max(self):
        self.assertEqual([dumpwmp.wmpRatingToStandard(r) for r in [0, 20, 40, 60, 80, 99]], [0, 20, 40, 60, 80, 100])

    def test_writes_five_stars_as_wmp_max(self):
        self.assertEqual([dumpwmp.standardRatingToWmp(r) for r in [0, 20, 40, 60, 80, 100]], [0, 20, 40, 60, 80, 99])

    def test_round_trips(self):
        for rating in [0, 20, 40, 60, 80, 100]:
            self.assertEqual(dumpwmp.wmpRatingToStandard(dumpwmp.standardRatingToWmp(rating)), rating)


@unittest.skipIf(dumpwmp is None, "Windows Media Player support needs pywin32")
class WMPParserTest(unittest.TestCase):
    def setUp(self):
        self.media = [FakeMedia("One", "1000", "80", "4"), FakeMedia("Two", "2000", "0", "")]
        wmp = mock.Mock()
        wmp.mediaCollection = FakeMediaCollection(self.media)
        patcher = mock.patch.object(dumpwmp.win32com.client, "Dispatch", return_value=wmp)
        patcher.start()
        self.addCleanup(patcher.stop)
        with quiet():
            self.parser = dumpwmp.WMPParser()
            self.songs = self.parser.getSongs()

    def test_reads_audio_items(self):
        self.assertEqual([s.title for s in self.songs], ["One", "Two"])
        one = self.songs[0]
        self.assertEqual((one.size, one.rating, one.playcount), ("1000", 80, 4))
        self.assertEqual(self.songs[1].playcount, 0)

    def test_songs_are_cached(self):
        self.assertIs(self.parser.getSongs(), self.songs)

    def test_writes_rating_and_playcount(self):
        one = self.songs[0]
        one.setRating(100)
        one.setPlaycount(9)
        self.assertEqual(self.media[0].written, {"UserRating": 99, "UserPlayCount": 9})


if __name__ == "__main__":
    unittest.main()
