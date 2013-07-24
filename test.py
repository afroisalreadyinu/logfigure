import unittest
import StringIO
import logging
from tempfile import NamedTemporaryFile
import uuid

from logfigure import load_config, LogLine

class LogfigureTests(unittest.TestCase):

    def test_basic(self):
        out_log = NamedTemporaryFile(suffix='.log')
        config = StringIO.StringIO("log all to %s" % out_log.name)
        load_config(config)
        logger = logging.getLogger('test')
        test_string = str(uuid.uuid4())
        logger.debug(test_string)
        with open(out_log.name, 'r') as log_out:
            self.failUnless(test_string in log_out.read())

class LogLineTests(unittest.TestCase):

    def test_source_can_be_omitted(self):
        ll = LogLine("log all to stdout")
        self.failUnlessEqual(ll.logger.level, "DEBUG")

    def test_source_can_be_all(self):
        ll = LogLine("log debug from all to stdout")
        self.failUnlessEqual(ll.logger.level, "DEBUG")
        self.failUnlessEqual(ll.logger.source, "")

    def test_source_pkg(self):
        ll = LogLine("log info from somepkg.blah to stdout")
        self.failUnlessEqual(ll.logger.level, "INFO")
        self.failUnlessEqual(ll.logger.source, "somepkg.blah")



if __name__ == "__main__":
    unittest.main()
