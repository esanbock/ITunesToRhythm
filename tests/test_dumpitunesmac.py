import platform
import unittest

import dumpitunesmac
import songparser
from helpers import quiet


class MacBackendTest(unittest.TestCase):
    def test_shares_base_classes(self):
        self.assertIs(dumpitunesmac.BaseSong, songparser.BaseSong)
        self.assertTrue(issubclass(dumpitunesmac.iTunesMacParser, songparser.BaseLibraryParser))

    @unittest.skipIf(platform.system() == "Darwin", "ScriptingBridge is available on macOS")
    def test_without_scriptingbridge_reports_no_songs(self):
        self.assertIsNone(dumpitunesmac.ScriptingBridge)
        with quiet():
            parser = dumpitunesmac.iTunesMacParser()
            self.assertEqual(parser.getSongs(), [])


if __name__ == "__main__":
    unittest.main()
