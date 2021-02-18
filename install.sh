#!/usr/bin/env sh

#Uses python magic vs realpath so it also works on a mac
FOLDER=$(python -c "import os; print(os.path.dirname(os.path.realpath('$0')))")
cd $FOLDER

# install in editable mode
pip3 install -e .

# used for rover command
yes | sudo pip3 install pexpect

# Install rover command
sudo ln -s $FOLDER/rover.py /usr/local/bin/rover
