import unittest
import StringIO
import logging
from tempfile import NamedTemporaryFile
import uuid

from logfigure import load_config, LogLine, Logconfig

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

    def test_split(self):
        out_log = NamedTemporaryFile(suffix='.log')
        config = StringIO.StringIO('''
log debug from all to stdout
log all from mypkg.submodule to ''' + out_log.name + ''' as "%(asctime)s - %(name)s - %(levelname)s - %(message)s"''')
        load_config(config)
        logger = logging.getLogger('test')
        stdout_string = str(uuid.uuid4())
        logger.debug(stdout_string)

        logger = logging.getLogger('mypkg.submodule')
        fileout_string = str(uuid.uuid4())
        logger.debug(fileout_string)
        with open(out_log.name, 'r') as log_out:
            contents = log_out.read()
            self.failIf(stdout_string in contents)
            self.failUnless(fileout_string in contents)


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

    def test_target_stdout(self):
        ll = LogLine("log info from somepkg to stdout")
        self.failUnlessEqual(ll.logger.handler.log_target,
                             'StreamHandler')
        self.failUnlessEqual(ll.logger.handler.class_args,
                             '(sys.stdout,)')

    def test_target_file(self):
        ll = LogLine("log info from somepkg to /some/path")
        self.failUnlessEqual(ll.logger.handler.log_target,
                             'FileHandler')
        self.failUnlessEqual(ll.logger.handler.class_args,
                             '("/some/path",)')

    def test_target_null(self):
        ll = LogLine("log info from somepkg to null")
        self.failUnlessEqual(ll.logger.handler.log_target,
                             'logfigure.NullHandler')
        self.failUnlessEqual(ll.logger.handler.class_args,
                             '()')

class LogconfigTests(unittest.TestCase):

    def test_root_set(self):
        config = StringIO.StringIO("""log debug from all to stdout
log info from test to /tmp/somefile.log""")
        logconfig = Logconfig(config)
        root_loggers = [x for x in logconfig.loggers if x.name == 'root']
        self.failUnlessEqual(len(root_loggers), 1)
        root_logger = root_loggers[0]
        self.failUnlessEqual(root_logger.level, 'DEBUG')
        self.failUnlessEqual(root_logger.handler.log_target, 'StreamHandler')

if __name__ == "__main__":
    unittest.main()
