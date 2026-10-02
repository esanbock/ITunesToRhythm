import contextlib
import io
import os
import shutil
import tempfile
import unittest

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
ITUNES_FIXTURE = os.path.join(FIXTURES, "itunes_library.xml")
RHYTHM_FIXTURE = os.path.join(FIXTURES, "rhythmdb.xml")


def quiet():
    """Swallow the program's console chatter during a test."""
    return contextlib.redirect_stdout(io.StringIO())


class TempLibraryTestCase(unittest.TestCase):
    """Gives each test its own writable copies of the fixture libraries."""

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tempdir)
        self.itunesPath = self.copyFixture(ITUNES_FIXTURE)
        self.rhythmPath = self.copyFixture(RHYTHM_FIXTURE)

    def copyFixture(self, path):
        return shutil.copy(path, self.tempdir)
