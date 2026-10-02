import io
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import iTunesToRhythm
from dumpitunes import iTunesLibraryParser
from dumprhythm import RhythmLibraryParser
from helpers import ITUNES_FIXTURE, RHYTHM_FIXTURE, TempLibraryTestCase, quiet


def songsByTitle(parserClass, path):
    with quiet():
        return {s.title: s for s in parserClass(path).getSongs()}


def runMain(*args):
    """Run the program with the given command line and return its output."""
    output = io.StringIO()
    with mock.patch.object(sys, "argv", ["iTunesToRhythm.py", *args]), redirect_stdout(output):
        iTunesToRhythm.main(sys.argv)
    return output.getvalue()


def summaryValue(output, name):
    for line in output.splitlines():
        if line.startswith(name + " = "):
            return int(line.split(" = ")[1])
    raise AssertionError(name + " not found in output")


class GetParserTest(TempLibraryTestCase):
    def test_detects_itunes_library(self):
        with quiet():
            self.assertIsInstance(iTunesToRhythm.getParser(ITUNES_FIXTURE, None), iTunesLibraryParser)

    def test_detects_rhythmbox_library(self):
        with quiet():
            self.assertIsInstance(iTunesToRhythm.getParser(RHYTHM_FIXTURE, None), RhythmLibraryParser)

    def test_rejects_unknown_format(self):
        path = os.path.join(self.tempdir, "other.xml")
        with open(path, "w") as f:
            f.write('<?xml version="1.0"?>\n<somethingelse/>\n')
        with quiet(), self.assertRaises(iTunesToRhythm.UnrecognizedFormatException):
            iTunesToRhythm.getParser(path, None)

    def test_missing_file(self):
        with quiet(), self.assertRaises(IOError):
            iTunesToRhythm.getParser(os.path.join(self.tempdir, "missing.xml"), None)


class SongCorrelatorTest(unittest.TestCase):
    def setUp(self):
        with quiet():
            self.correlator = iTunesToRhythm.SongCorrelator(iTunesLibraryParser(ITUNES_FIXTURE))
        self.rhythmSongs = songsByTitle(RhythmLibraryParser, RHYTHM_FIXTURE)

    def correlate(self, title, useSongTitle=False):
        with quiet():
            return self.correlator.correlateSong(self.rhythmSongs[title], False, False, useSongTitle, False)

    def test_full_match_by_size(self):
        match = self.correlate("Song A")
        self.assertEqual(match.title, "Song A")
        self.assertEqual(self.correlator.fullMatches, 1)

    def test_disambiguates_same_size_by_title(self):
        match = self.correlate("Twin Two")
        self.assertEqual(match.title, "Twin Two")
        self.assertEqual(self.correlator.fullMatches, 1)
        self.assertEqual(self.correlator.ambiguousMatches, 0)

    def test_no_match(self):
        self.assertIsNone(self.correlate("Orphan"))
        self.assertEqual(self.correlator.zeroMatches, 1)

    def test_match_by_title(self):
        match = self.correlate("Song B", useSongTitle=True)
        self.assertEqual(match.size, "2000002")


class MainTest(TempLibraryTestCase):
    def rhythmSongs(self):
        return songsByTitle(RhythmLibraryParser, self.rhythmPath)

    def itunesSongs(self):
        return songsByTitle(iTunesLibraryParser, self.itunesPath)

    def test_dry_run_reports_but_does_not_write(self):
        with open(self.rhythmPath, "rb") as f:
            before = f.read()
        output = runMain(self.itunesPath, self.rhythmPath)
        with open(self.rhythmPath, "rb") as f:
            self.assertEqual(f.read(), before)
        self.assertEqual(summaryValue(output, "full matches"), 3)
        self.assertEqual(summaryValue(output, "no matches"), 1)
        self.assertEqual(summaryValue(output, "output modifications"), 3)
        self.assertIn("Changes were not written", output)

    def test_writes_ratings_and_playcounts(self):
        runMain("-w", self.itunesPath, self.rhythmPath)
        songs = self.rhythmSongs()
        self.assertEqual((songs["Song A"].rating, songs["Song A"].playcount), (80, 5))
        self.assertEqual((songs["Twin Two"].rating, songs["Twin Two"].playcount), (40, 3))
        # unrated, unplayed source song leaves the destination alone
        self.assertEqual((songs["Song B"].rating, songs["Song B"].playcount), (0, 0))
        # unmatched song is untouched
        self.assertEqual((songs["Orphan"].rating, songs["Orphan"].playcount), (0, 0))

    def test_noratings(self):
        runMain("-w", "--noratings", self.itunesPath, self.rhythmPath)
        song = self.rhythmSongs()["Song A"]
        self.assertEqual((song.rating, song.playcount), (40, 5))

    def test_noplaycounts(self):
        runMain("-w", "--noplaycounts", self.itunesPath, self.rhythmPath)
        song = self.rhythmSongs()["Song A"]
        self.assertEqual((song.rating, song.playcount), (80, 1))

    def test_dateadded(self):
        runMain("-w", "--dateadded", self.itunesPath, self.rhythmPath)
        self.assertEqual(self.rhythmSongs()["Song A"].dateadded, self.itunesSongs()["Song A"].dateadded)

    def test_twoway_copies_higher_playcount_back_to_source(self):
        with quiet():
            parser = RhythmLibraryParser(self.rhythmPath)
            {s.title: s for s in parser.getSongs()}["Song A"].setPlaycount(10)
            parser.save()

        output = runMain("-w", "--twoway", self.itunesPath, self.rhythmPath)

        itunesSongA = self.itunesSongs()["Song A"]
        self.assertEqual((itunesSongA.rating, itunesSongA.playcount), (40, 10))
        rhythmSongA = self.rhythmSongs()["Song A"]
        self.assertEqual((rhythmSongA.rating, rhythmSongA.playcount), (40, 10))
        self.assertEqual(summaryValue(output, "input modifications"), 1)
        self.assertIn("Changes were written to source", output)


class CommandLineTest(unittest.TestCase):
    def parse(self, *args):
        with mock.patch.object(sys, "argv", ["iTunesToRhythm.py", *args]):
            return iTunesToRhythm.processCommandLine(sys.argv)

    def test_defaults(self):
        options, args = self.parse("in.xml", "out.xml")
        self.assertEqual(args, ["in.xml", "out.xml"])
        self.assertFalse(options.writeChanges)
        self.assertFalse(options.twoway)
        self.assertFalse(options.useSongTitle)

    def test_requires_source_and_destination(self):
        with quiet(), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.parse("in.xml")

    def test_rejects_same_source_and_destination(self):
        with quiet(), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.parse("same.xml", "same.xml")


if __name__ == "__main__":
    unittest.main()
