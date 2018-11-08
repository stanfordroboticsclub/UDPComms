#!/usr/bin/env sh

#The `clean --all` removes the build directory automaticly which makes reinstalling new versions possbile with the same command.
python setup.py clean --all install
python3 setup.py clean --all install
