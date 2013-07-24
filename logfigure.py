import os, sys
import re

class ParseError(Exception): pass

class Bunch(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

level_synonyms = {
    "all": "DEBUG"
}

try:
    from logging import NullHandler
    NULLHANDLER = 'NullHandler'
except ImportError:
    import logging
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
    NULLHANDLER = 'logfigure.NullHandler'

#todo  qualname for log_from
#todo  tests

class LogLine(object):

    def __init__(self, line):
        self.log = False
        self.log_level       = None
        self.log_from        = None
        self.log_from_prefix = None
        self.log_where       = None
        self.log_as_prefix   = None
        self.log_as          = None
        self.log_to_prefix   = False
        self.parse(line)
        self.logger = self.build_components()

    def replace_quoted(self, line):
        quoted_index = 0
        quoted_dict = {}
        for quoted in re.finditer('"[^"]*"', line):
            quoted_string = quoted.group()
            quoted_placeholder = 'QUOTED%d' % quoted_index
            quoted_dict[quoted_placeholder] = quoted_string
            line = line.replace(quoted_string, quoted_placeholder)
        return line, quoted_dict

    def parse(self, line):
        line, quoted_dict = self.replace_quoted(line)
        parts = line.split()
        parts.reverse()
        while parts:
            part = parts.pop()
            if not self.log:
                if not part == 'log':
                    raise ParseError('Line must begin with log')
                else:
                    self.log = True
            elif not self.log_level:
                self.log_level = (level_synonyms[part]
                                  if part in level_synonyms
                                  else part.upper())

            elif not self.log_from_prefix:
                if part not in ["to", "from"]:
                    raise ParseError('Log level should be followed either by from or to')
                self.log_from_prefix = True
                if part == 'to':
                    self.log_from = ''
                    parts.append(part)
            elif self.log_from is None:
                self.log_from = '' if part == 'all' else part
            elif not self.log_to_prefix:
                if part != "to":
                    raise ParseError('Log location should be preceded with "to"')
                self.log_to_prefix = True

            elif not self.log_where:
                self.log_where = part
            elif not self.log_as_prefix:
                if part != "as":
                    raise ParseError('Log format should be preceded with "as"')
                self.log_as_prefix = True
            else:
                self.log_as = quoted_dict[part][1:-1]


    def __repr__(self):
        return "Log what: %s  where: %s  as: %s" % (self.log_level,
                                                    self.log_where,
                                                    self.log_as)

    def build_components(self):
        replacement_re = re.compile("\W*")
        base_name = "%s_%s" % (replacement_re.sub('', self.log_where),
                               self.log_level)
        if self.log_as:
            formatter = Formatter(base_name, self.log_as)
        else:
            formatter = None
        handler = Handler(base_name, self.log_where, self.log_level, formatter)
        return Logger(base_name, self.log_level, self.log_from, handler)


class Logger(object):
    def __init__(self, name, level, source, handler):
        self.name = name
        self.level = level
        self.handler = handler
        self.source = source

    def __str__(self):
        section = """
[logger_%(name)s]
level=%(level)s
handlers=%(handler)s
""" % dict(name=self.name, level=self.level, handler=self.handler.name)
        if self.source:
            section += "qualname=%s\n" % self.source
        return section



class Handler(object):
    def __init__(self, name, log_target, level, formatter):
        self.name = name
        self.class_args = '()'
        if log_target == 'stdout':
            self.log_target = 'StreamHandler'
            self.class_args = '(sys.stdout,)'
        elif log_target.startswith('/'): #TODO correct this hack
            self.log_target = 'FileHandler'
            self.class_args = '("%s",)' % log_target
        elif log_target == 'null': #TODO correct this hack
            self.log_target = NULLHANDLER
        self.level = level
        self.formatter = formatter

    def __str__(self):
        section = """
[handler_%(name)s]
level=%(level)s
class=%(log_target)s
args=%(class_args)s
""" % self.__dict__
        if self.formatter:
            section += "formatter=%s\n" % self.formatter.name
        return section


class Formatter(object):
    def __init__(self, name, logformat):
        self.name = name
        self.logformat = logformat

    def __str__(self):
        return """
[formatter_%(name)s]
format=%(logformat)s
datefmt=
""" % self.__dict__


class Logconfig(object):
    def __init__(self, cfg_path):
        if hasattr(cfg_path, 'readlines'):
            lines = [x.strip() for x in cfg_path.readlines()]
        else:
            cfg_path = os.path.abspath(cfg_path)
            assert os.path.exists(cfg_path), "No config file at %" % cfg_path
            with open(cfg_path, 'r') as inp_file:
                lines = [x.strip() for x in inp_file.readlines()]
        self.loglines = [LogLine(line) for line in lines
                         if not line.startswith('#')]
        for logline in self.loglines:
            if logline.log_from == '':
                logline.logger.name = 'root'
                break

    @property
    def loggers(self):
        return [x.logger for x in self.loglines]

    @property
    def handlers(self):
        return [x.logger.handler for x in self.loglines]

    @property
    def formatters(self):
        return [x.logger.handler.formatter for x in self.loglines
                if x.logger.handler.formatter] #TODO fix this


    @property
    def header(self):
        loggers = ','.join(x.name for x in self.loggers)
        handlers = ','.join(x.name for x in self.handlers)
        formatters = ','.join(x.name for x in self.formatters)
        return """
[loggers]
keys=%s
[handlers]
keys=%s
[formatters]
keys=%s
""" % (loggers, handlers, formatters)

    def __str__(self):
        return "\n".join([self.header] +
                         [str(x) for x in self.loggers] +
                         [str(x) for x in self.handlers] +
                         [str(x) for x in self.formatters])



def print_config():
    if not len(sys.argv) == 2:
        print "Usage: logfigure LOGFILE-NAME"
        return
    logconfig = Logconfig(sys.argv[1])
    print str(logconfig)

def load_config(base_file):
    logconfig = Logconfig(base_file)
    import logging.config
    import StringIO
    logging.config.fileConfig(StringIO.StringIO(str(logconfig)))

if __name__ == "__main__":
    #load_config(sys.argv[1])
    print_config(sys.argv[1])
