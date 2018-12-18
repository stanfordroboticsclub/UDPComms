#!/usr/bin/env python3

import sys
import UDPComms
import json

if ( len(sys.argv) != 2):
    print("Usage: \n rover peek port_number")
    print("TODO Usage: \n rover poke port_number rate")
    exit()

port = int(sys.argv[1])
sub = UDPComms.Subscriber(port, timeout = 10)

# peek
while 1:
    try:
        print( json.dumps(sub.recv()) )
    except UDPComms.timeout:
        exit()

# poke
while 1:
    line = sys.stdin.readline()
    if line=="":
        continue
    print(line.rstrip('\n'))



