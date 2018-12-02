#!/usr/bin/env sh

#The `clean --all` removes the build directory automaticly which makes reinstalling new versions possbile with the same command.

FOLDER=$(dirname $(realpath "$0"))

cd $FOLDER
python setup.py clean --all install
python3 setup.py clean --all install
