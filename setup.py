import os
from setuptools import setup, find_packages

dependencies = []

setup(
    name = "logfigure",
    version = "0.01",
    author = "Ulas Tuerkmen",
    author_email = "ulas.tuerkmen@gmail.com",
    description = ("Logging configuration that respects your sanity"),
    install_requires = dependencies,
    packages=find_packages(),
    entry_points = {'console_scripts': ['logfigure = logfigure:print_config']}
)
