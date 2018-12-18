#!/usr/bin/env python3

import sys
import UDPComms

if ( len(sys.argv) != 2):
    print("Usage: \n peek port_number")
    exit()

port = int(sys.argv[1])
sub = UDPComms.Subscriber(port, timeout = 10)

while 1:
    try:
        print(sub.recv())
    except UDPComms.timeout:
        exit()
