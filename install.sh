#!/usr/bin/env sh

#Uses python magic vs realpath so it also works on a mac
FOLDER=$(python -c "import os; print(os.path.dirname(os.path.realpath('$0')))")
cd $FOLDER

#forces 0.6.0 until I update to new msgpack version
yes | sudo pip2 install -Iv msgpack==0.6.0
yes | sudo pip3 install -Iv msgpack==0.6.0


#The `clean --all` removes the build directory automatically which makes reinstalling new versions possible with the same command.
python2 setup.py clean --all install
python3 setup.py clean --all install

# used for rover command
yes | sudo pip3 install pexpect

# Install rover command
sudo ln -s $FOLDER/rover.py /usr/local/bin/rover
