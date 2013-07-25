import os
from setuptools import setup

dependencies = []

setup(
    name = "logfigure",
    version = "0.01",
    author = "Ulas Tuerkmen",
    author_email = "ulas.tuerkmen@gmail.com",
    description = ("Logging configuration that respects your sanity"),
    install_requires = dependencies,
    packages=['logfigure'],
    entry_points = {'console_scripts': ['logfigure = logfigure:print_config']},
    url = "https://github.com/afroisalreadyinu/logfigure",
)
