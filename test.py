import unittest
import StringIO
import logging
from tempfile import NamedTemporaryFile
import uuid

from logfigure import load_config

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


if __name__ == "__main__":
    unittest.main()
