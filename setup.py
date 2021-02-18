#!/usr/bin/env python

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

exec(open(HERE / "UDPComms/version.py").read())

setup(name='UDPComms',
      version=__version__,
      description='Simple library for sending messages over UDP',
      long_description=README,
      long_description_content_type="text/markdown",
      author='Michal Adamkiewicz',
      author_email='mikadam@stanford.edu',
      license='MIT',
      url='https://github.com/stanfordroboticsclub/UDP-Comms',
      packages=['UDPComms'],
      install_requires=["msgpack>=1.0.0"],
     )
