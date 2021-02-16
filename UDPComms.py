
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

from sys import version_info

USING_PYTHON_2 = (version_info[0] < 3)
if USING_PYTHON_2:
    from time import time as monotonic
else:
    from time import monotonic

timeout = socket.timeout

MAX_SIZE = 65507
DEFAULT_MULTICAST = "239.255.20.22"
DEFAULT_BROADCAST = "10.0.0.255"

##TODO:
# Test on ubuntu and debian
# Documentation (targets, and security disclaimer)

class Scope(Enum):
    LOCAL = auto()
    NETWORK = auto()
    BROADCAST = auto()

class Publisher:
    MULTICAST_IP = DEFAULT_MULTICAST
    BROADCAST_IP = DEFAULT_BROADCAST

    def __init__(self, port, scope = Scope.NETWORK):
        """ Create a Publisher Object

        Arguments:
            port         -- the port to publish the messages on
            scope        -- the scope the messages will be sent to
        """

        self.sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.scope = scope
        self.port  = port

        if self.scope == Scope.BROADCAST:
            ip = self.BROADCAST_IP
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        else:
            ip = self.MULTICAST_IP
            if self.scope == Scope.LOCAL:
                ttl = 0
            elif self.scope == Scope.NETWORK:
                ttl = 1
            else:
                raise ValueError("Unknown Scope")

            self.sock.setsockopt(socket.IPPROTO_IP,
                                 socket.IP_MULTICAST_TTL,
                                 struct.pack('b', ttl))


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
    BROADCAST_IP = DEFAULT_BROADCAST

    def __init__(self, port, timeout=0.2, scope = Scope.NETWORK ):
        """ Create a Subscriber Object

        Arguments:
            port         -- the port to listen to messages on
            timeout      -- how long to wait before a message is considered out of date
            scope        -- where to expect messages to come from
        """
        self.scope = scope
        self.port = port
        self.timeout = timeout

        self.last_data = None
        self.last_time = float('-inf')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        if self.scope == Scope.BROADCAST:
            ip = self.BROADCAST_IP
            bind_ip = self.BROADCAST_IP
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        elif self.scope == Scope.LOCAL or self.scope == Scope.NETWORK:
            ip = self.MULTICAST_IP
            bind_ip = "0.0.0.0"
            mreq = struct.pack("4sl", socket.inet_aton(ip), socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        else:
            raise ValueError("Unknown Scope")

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
