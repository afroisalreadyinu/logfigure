Logfigure generates logging configuration for the Python logging
standard library. The accepted format is a very simple DSL close to
natural language, and configuration in the file configuration format
is generated. You can also use logfigure as a library to configure
logging directly from the accepted format.

Logfigure accepts a file consisting of lines that specify what to log
where and in which format. The simplest configuration line is the
following:

    log all to null

This creates a root logger with a null handler, and all levels are
logged to it. The general format accepted by logfigure is as follows:

    log LEVEL from PKG to TARGET as FORMAT

LEVEL should be self-explanatory; it can be either `all` or one of the
standard logging levels. PKG refers to the hierarchical name of the
logger, which can later be used to get the logger with
`logging.getLogger(__name__)`. TARGET specifies how to log. It can be
one of null (which leads to NullHandler), path to a file (FileHandler)
and stdout (StreamHandler with `sys.stdout` as output stream). The `as
FORMAT` part can be ommitted, which leads to the standard formatter
getting used. If included, FORMAT should be a valid string formatting
for a
[LogRecord](http://docs.python.org/2/library/logging.html#logging.LogRecord). An example:

    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

To convert a configuration file in this format, run `logfigure
cfg_file_path`. This will print the converted data into standard
out. In order to configure logging from a file, use
`logfigure.load_config`.