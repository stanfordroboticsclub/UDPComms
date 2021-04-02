
"""
This is a simple library to enable communication between different processes (potentially on different machines) over a network using UDP. It's goals a simplicity and easy of understanding and reliability

mikadam@stanford.edu
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import socket
import struct
from enum import Enum, auto

import msgpack
import netifaces

from sys import version_info

USING_PYTHON_2 = (version_info[0] < 3)
if USING_PYTHON_2:
    from time import time as monotonic
else:
    from time import monotonic

timeout = socket.timeout

MAX_SIZE = 65507
DEFAULT_MULTICAST = "239.255.20.22"

##TODO:
# Test on ubuntu and debian
# Documentation (targets, and security disclaimer)

def get_iface_info(target):
    if target in netifaces.interfaces():
        return netifaces.ifaddresses(target)[netifaces.AF_INET][0]

    else:
        for iface in netifaces.interfaces():
            for addr in netifaces.ifaddresses(iface)[socket.AF_INET]:
                if target == addr['addr']:
                    return addr

    ValueError("target needs to be valid interface name or interface ip")

class Publisher:
    MULTICAST_IP = DEFAULT_MULTICAST

    def __init__(self, port, target = "127.0.0.1", use_multicast = True):
        """ Create a Publisher Object

        Arguments:
            port          -- the port to publish the messages on
            target        -- name or ip of interface to sent messages to
            use_multicast -- use multicast transport instead of broadcast
        """

        self.iface = get_iface_info(target)

        if self.iface['addr'] == "127.0.0.1" and not use_multicast:
            raise ValueError("Broadcast not supported on lo0")

        self.sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port  = port

        if use_multicast:
            ip = self.MULTICAST_IP
            ttl = 1 # local is restricted by interface so ttl can just be 1

            self.sock.setsockopt(socket.IPPROTO_IP,
                                 socket.IP_MULTICAST_TTL,
                                 struct.pack('b', ttl))

            self.sock.setsockopt(socket.IPPROTO_IP,
                                 socket.IP_MULTICAST_IF,
                                 socket.inet_aton(self.iface['addr']));
        else:
            ip = self.iface['broadcast']
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


        self.sock.settimeout(0.2)
        self.sock.connect((ip, port))

    def send(self, obj):
        """ Publish a message. The obj can be any nesting of standard python types """
        msg = msgpack.dumps(obj, use_bin_type= not USING_PYTHON_2)
        assert len(msg) < MAX_SIZE, "Encoded message too big!"
        self.sock.send(msg)

    def __del__(self):
        self.sock.close()


class Subscriber:
    MULTICAST_IP = DEFAULT_MULTICAST

    def __init__(self, port, timeout=0.2, target = "127.0.0.1", use_multicast = True ):
        """ Create a Subscriber Object

        Arguments:
            port          -- the port to listen to messages on
            timeout       -- how long to wait before a message is considered out of date
            target        -- the name or address of interface from which to recv messages
            use_multicast -- use multicast transport instead of broadcast
        """
        self.port = port
        self.timeout = timeout

        self.last_data = None
        self.last_time = float('-inf')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        if target in ("", "all", "ALL", "0.0.0.0"):
            if not use_multicast:
                raise ValueError("broadcast can't listen to all interfaces")

            self.iface = {'addr':"0.0.0.0"}
        else:
            self.iface = get_iface_info(target)

        if use_multicast:
            bind_ip = self.MULTICAST_IP
            mreq = struct.pack("=4s4s", socket.inet_aton(self.MULTICAST_IP),
                                        socket.inet_aton(self.iface['addr']))
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        else:
            bind_ip = self.iface['broadcast'] #binding to interface address doesn't work
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.sock.settimeout(timeout)
        self.sock.bind((bind_ip, port))

    def recv(self):
        """ Receive a single message from the socket buffer. It blocks for up to timeout seconds.
        If no message is received before timeout it raises a UDPComms.timeout exception"""

        try:
            self.last_data, address = self.sock.recvfrom(MAX_SIZE)
        except BlockingIOError:
            raise socket.timeout("no messages in buffer and called with timeout = 0")

        self.last_time = monotonic()
        return msgpack.loads(self.last_data, raw=USING_PYTHON_2)

    def get(self):
        """ Returns the latest message it can without blocking. If the latest massage is 
            older then timeout seconds it raises a UDPComms.timeout exception"""
        try:
            self.sock.settimeout(0)
            while True:
                self.last_data, address = self.sock.recvfrom(MAX_SIZE)
                self.last_time = monotonic()
        except socket.error:
            pass
        finally:
            self.sock.settimeout(self.timeout)

        current_time = monotonic()
        if (current_time - self.last_time) < self.timeout:
            return msgpack.loads(self.last_data, raw=USING_PYTHON_2)
        else:
            raise socket.timeout("timeout=" + str(self.timeout) + \
                                 ", last message time=" + str(self.last_time) + \
                                 ", current time=" + str(current_time))

    def get_list(self):
        """ Returns list of messages, in the order they were received"""
        msg_bufer = []
        try:
            self.sock.settimeout(0)
            while True:
                self.last_data, address = self.sock.recvfrom(MAX_SIZE)
                self.last_time = monotonic()
                msg = msgpack.loads(self.last_data, raw=USING_PYTHON_2)
                msg_bufer.append(msg)
        except socket.error:
            pass
        finally:
            self.sock.settimeout(self.timeout)

        return msg_bufer

    def __del__(self):
        self.sock.close()


if __name__ == "__main__":
    msg = 'very important data'

    a = Publisher(1000)
    a.send( {"text": "magic", "number":5.5, "bool":False} )
