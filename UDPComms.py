
"""
This is a simple library to enable communication between different processes (potentially on different machines) over a network using UDP. It's goals a simplicity and easy of understanding and reliability

mikadam@stanford.edu
"""
import socket
import struct
from collections import namedtuple

class Publisher:
    broadcast_ip = "10.0.0.255"
    def __init__(self, fields, typ, port):
        """ Create a Publisher Object

        Arguments:
            fields       -- tuple of human readable names of fields in the message
            typ          -- a struct format string that described the low level message layout
            port         -- the port to publish the messages on
        """
        self.struct = struct.Struct(typ)
        self.tuple = namedtuple("msg", fields)

        assert len(self.tuple._fields) == \
               len(self.struct.unpack( "0"*self.struct.size ))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.sock.settimeout(0.2)
        self.sock.connect((self.broadcast_ip, port))


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
    def __init__(self, fields, typ, port):
        """ Create a Subscriber Object

        Arguments:
            fields       -- tuple of human readable names of fields in the message
            typ          -- a struct format string that described the low level message layout
            port         -- the port to listen to messages on
        """
        self.struct = struct.Struct(typ)
        self.tuple = namedtuple("msg", fields)

        assert len(self.tuple._fields) == \
               len(self.struct.unpack( "0"*self.struct.size ))


        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.sock.bind(("", port))

    def recv(self):
        """ Recive a message. Returns a namedtuple matching the messages fieldnames """
        data, address = self.sock.recvfrom(self.struct.size)
        print 'received %s bytes from %s' % (len(data), address)
        return self.tuple(*self.struct.unpack(data))

    def debug_recv_type(self):
        """ Verify the message type matches the publisher """
        data, address = self.sock.recvfrom(2048)

        fields = data.split(",")
        print fields
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
