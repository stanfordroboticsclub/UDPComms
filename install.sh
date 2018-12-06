#!/usr/bin/env sh

#Uses python magic vs realpath so it also works on a mac
FOLDER=$(python -c "import os; print(os.path.dirname(os.path.realpath('$0')))")
cd $FOLDER

yes | sudo pip install msgpack
yes | sudo pip3 install msgpack

#The `clean --all` removes the build directory automaticly which makes reinstalling new versions possbile with the same command.
python setup.py clean --all install
python3 setup.py clean --all install
