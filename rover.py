#!/usr/bin/env python3

import sys
import argparse
import json
import time
import select
import pexpect

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
    pub = UDPComms.Publisher(port)
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

def call_func(command):
    child = pexpect.spawn(command)

    i = 1
    while i == 1:
        try:
            i = child.expect(['password:', 
                         'Are you sure you want to continue connecting'], timeout=20)
        except pexpect.EOF:
            print("Can't connect to device")
            exit()
        except pexpect.TIMEOUT:
            print("Interaction with device failed")
            exit()

        if i == 1:
            child.sendline('yes')

    child.sendline('raspberry')
    child.interact()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser')

    peek = subparsers.add_parser("peek")
    peek.add_argument('port', help="UDP port to subscribe to", type=int)

    poke = subparsers.add_parser("poke")
    poke.add_argument('port', help="UDP port to publish the data to", type=int)
    poke.add_argument('rate', help="how often to republish (ms)", type=float)

    commands = ['status', 'log', 'start', 'stop', 'restart', 'enable', 'disable']
    for command in commands:
        status = subparsers.add_parser(command)
        status.add_argument('host', help="Which device to look for this program on")
        status.add_argument('unit', help="The unit whose status we want to know", 
                                                        nargs='?', default=None)

    args = parser.parse_args()

    if args.subparser == 'peek':
        peek_func(args.port)
    elif args.subparser == 'poke':
        poke_func(args.port, args.rate)

    elif args.subparser in commands:
        if args.unit is None:
            args.unit = args.host

        if args.subparser == 'status':
            call_func("ssh pi@"+args.host+".local"+" sudo systemctl status "+args.unit)
        elif args.subparser == 'log':
            call_func("ssh pi@"+args.host+".local"+" sudo journalctl -f -u "+args.unit)
        elif args.subparser == 'start':
            call_func("ssh pi@"+args.host+".local"+" sudo systemctl start "+args.unit)
        elif args.subparser == 'stop':
            call_func("ssh pi@"+args.host+".local"+" sudo systemctl stop "+args.unit)
        elif args.subparser == 'restart':
            call_func("ssh pi@"+args.host+".local"+" sudo systemctl restart "+args.unit)
        elif args.subparser == 'enable':
            call_func("ssh pi@"+args.host+".local"+" sudo systemctl enable "+args.unit)
        elif args.subparser == 'disable':
            call_func("ssh pi@"+args.host+".local"+" sudo systemctl disable "+args.unit)
    else:
        parser.print_help()

