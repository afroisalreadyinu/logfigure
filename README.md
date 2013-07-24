Logfigure generates loggign configuration for the Python logging
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
