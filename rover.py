#!/usr/bin/env python3

import sys
import argparse
import json
import time
import select

import UDPComms
import msgpack


def peek_func(port):
    sub = UDPComms.Subscriber(port, timeout = 10)
    while 1:
        try:
            data = sub.recv()
            # ugly but works for now
            no_bytes = msgpack.loads(msgpack.dumps(data), encoding='utf-8')
            print( json.dumps(no_bytes) )
        except UDPComms.timeout:
            exit()

def poke_func(port, rate):
    pub = UDPComms.Publisher(port, local = True)
    data = None

    while 1:
        if select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            # detailed behaviour
            # reading from file: -ignores empty lines -repeats last line forever
            # reading from terminal: -repeats last command
            if line.rstrip():
                data = line.rstrip()
            elif len(line) == 0:
                # exit() #uncomment to quit on end of file
                pass
            else:
                continue

        if data != None:
            pub.send( json.loads(data) )
            time.sleep( rate/1000 )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser')

    peek = subparsers.add_parser("peek")
    peek.add_argument('port', help="UDP port to subscribe to", type=int)

    poke = subparsers.add_parser("poke")
    poke.add_argument('port', help="UDP port to publish the data to", type=int)
    poke.add_argument('rate', help="how often to republish (ms)", type=float)

    args = parser.parse_args()

    if args.subparser == 'peek':
        peek_func(args.port)
    elif args.subparser == 'poke':
        poke_func(args.port, args.rate)
    else:
        parser.print_help()





