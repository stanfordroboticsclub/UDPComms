
"""
This is a simple library to enable communication between different processes (potentially on different machines) over a network using UDP. It's goals a simplicity and easy of understanding and reliability

mikadam@stanford.edu
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import socket
import struct
from collections import namedtuple

from sys import version_info
if version_info[0] < 3:
    from time import time as monotonic
else:
    from time import monotonic

timeout = socket.timeout

class Publisher:
    def __init__(self, fields, typ, port, local = False):
        """ Create a Publisher Object

        Arguments:
            fields       -- tuple of human readable names of fields in the message
            typ          -- a struct format string that described the low level message layout
            port         -- the port to publish the messages on
            local        -- if True publisher will only publish to only this computer but it will 
                            work even if the computer isn't connected to a rover network. Useful for
                            development
        """
        self.broadcast_ip = "10.0.0.255"

        self.struct = struct.Struct(typ)
        self.tuple = namedtuple("msg", fields)

        assert len(self.tuple._fields) == \
               len(self.struct.unpack( b"0"*self.struct.size ))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if(not local):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.broadcast_ip = "127.0.0.1"

        self.sock.settimeout(0.2)
        self.sock.connect((self.broadcast_ip, port))

        self.port = port
        self.local = local


    def send(self, *arg, **kwarg):
        """ Publish a message. The arguments are the message fields """
        msg = self.tuple(*arg, **kwarg)
        data = self.struct.pack(*msg)
        self.sock.send(data)

    def debug_send_type(self):
        """ Send the message type to be verified """
        data_to_send = self.struct.format + "," + ",".join(self.tuple._fields)
        assert len(data_to_send) < 2048
        self.sock.send(data_to_send)

    def __del__(self):
        self.sock.close()


class Subscriber:
    def __init__(self, fields, typ, port, timeout=0.2):
        """ Create a Subscriber Object

        Arguments:
            fields       -- tuple of human readable names of fields in the message
            typ          -- a struct format string that described the low level message layout
            port         -- the port to listen to messages on
            timeout      -- how long to wait before a message is considered out of date
        """
        self.fields = fields
        self.typ = typ
        self.port = port
        self.timeout = timeout

        self.struct = struct.Struct(typ)
        self.tuple = namedtuple("msg", fields)
        self.str_coding = str(c for c in typ if c in "sm")

        self.last_message = None
        self.last_time = float('-inf')

        assert len(self.tuple._fields) == \
               len(self.struct.unpack( b"0"*self.struct.size ))


        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.sock.settimeout(timeout)
        self.sock.bind(("", port))

    def parse_message(self, data):
        if self.str_coding = "":
            return self.tuple(*self.struct.unpack(data))
        else:
            out = []
            i = 0
            for elem in self.struct.unpack(data):
                if type(elem) == bytes:
                    if self.str_coding[i] == 's':
                        out.append(elem.rstrip(b'\0')
                    else:
                        unpacker = msgpack.Unpacker()
                        unpacker.feed(elem)
                        out.append(unpacker.unpack())
                    i+=1
                else:
                    out.append(elem)
            return self.tuple(*out)

    def recv(self):
        """ Receive a message. Returns a namedtuple matching the messages fieldnames 
            If no message is received before timeout it raises a UDPComms.timeout exception"""
        data, address = self.sock.recvfrom(self.struct.size)
        #print('received %s bytes from %s' % (len(data), address))
        self.last_message = self.parse_message(data)
        self.last_time = monotonic()
        return self.last_message

    def get(self):
        """ Returns the latest message it can without blocking. If the latest massage is 
            older then timeout seconds it raises a UDPComms.timeout exception"""
        try:
            self.sock.settimeout(0)
            while True:
                self.recv()
        except socket.error:
            pass
        finally:
            self.sock.settimeout(self.timeout)

        current_time = monotonic()
        if (current_time - self.last_time) < self.timeout:
            return self.last_message
        else:
            raise socket.timeout("timeout=" + str(self.timeout) + \
                                 ", last message time=" + str(self.last_time) + \
                                 ", current time=" + str(current_time))

    def debug_recv_type(self):
        """ Verify the message type matches the publisher """
        data, address = self.sock.recvfrom(2048)

        fields = data.split(",")
        print(fields)
        format_ = fields.pop(0)

        assert format_ == self.struct.format
        assert tuple(fields) == self.tuple._fields

        return True

    def __del__(self):
        self.sock.close()


params = ("left right", 'ff', 10000)

if __name__ == "__main__":
    msg = 'very important data'

    a = Publisher(*params)
    a.send(ip, msg)
