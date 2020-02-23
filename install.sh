#!/usr/bin/env sh

#Uses python magic vs realpath so it also works on a mac
FOLDER=$(python -c "import os; print(os.path.dirname(os.path.realpath('$0')))")
cd $FOLDER

#forces 0.6.0 until I update to new msgpack version
yes | sudo pip install -Iv msgpack==0.6.0
yes | sudo pip3 install -Iv msgpack==0.6.0

# used for rover command
yes | sudo pip3 install pexpect

#The `clean --all` removes the build directory automaticly which makes reinstalling new versions possbile with the same command.
python setup.py clean --all install
python3 setup.py clean --all install

# Install rover command
sudo ln -s $FOLDER/rover.py /usr/local/bin/rover
