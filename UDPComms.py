
"""
This is a simple library to enable communication between different processes (potentially on different machines) over a network using UDP multicasting. It's goals a simplicity and easy of understanding and reliability

mikadam@stanford.edu
"""
import socket
import struct
from collections import namedtuple

class Publisher:
    my_ip = "10.0.0.11"
    def __init__(self, fields, typ, multicast_ip, port):
        """ Create a Publisher Object

        Arguments:
            fields       -- tuple of human readable names of fields in the message
            typ          -- a struct format string that described the low level message layout
            multicast_ip -- the multicast group to publish the messages to
            port         -- the port to publish the messages on
        """
        self.struct = struct.Struct(typ)
        self.tuple = namedtuple("msg", fields)

        assert len(self.tuple._fields) == \
               len(self.struct.unpack( "0"*self.struct.size ))

        self.multicast_group = (multicast_ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.settimeout(0.2)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
        self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.my_ip))

        self.sock.connect(self.multicast_group)

    def send(self, *arg, **kwarg):
        """ Publish a message. The arguemnts are the message fields """
        msg = self.tuple(*arg, **kwarg)
        data = self.struct.pack(*msg)
        self.sock.send(data)

    def debug_send_type(self):
        """ Send the message type to be verified """
        self.sock.send(self.struct.format + "," + ",".join(self.tuple._fields) )

    def __del__(self):
        self.sock.close()


class Subscriber:
    def __init__(self, fields, typ, multicast_ip, port):
        """ Create a Subscriber Object

        Arguments:
            fields       -- tuple of human readable names of fields in the message
            typ          -- a struct format string that described the low level message layout
            multicast_ip -- the multicast group to subscriber to messages on
            port         -- the port to listen to messages on
        """
        self.struct = struct.Struct(typ)
        self.tuple = namedtuple("msg", fields)

        assert len(self.tuple._fields) == \
               len(self.struct.unpack( "0"*self.struct.size ))

        self.multicast_group = multicast_ip
        self.server_address = ('', port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_address)

        # Tell the operating system to add the socket to the multicast group
        # on all interfaces.
        group = socket.inet_aton(self.multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def recv(self):
        """ Recive a message. Returns a namedtuple matching the messages fieldnames """
        data, address = self.sock.recvfrom(1024)
        print 'received %s bytes from %s' % (len(data), address)
        return self.tuple(*self.struct.unpack(data))

    def debug_recv_type(self):
        """ Verify the message type matches the publisher """
        data, address = self.sock.recvfrom(1024)

        fields = data.split(",")
        print fields
        format_ = fields.pop(0)

        assert format_ == self.struct.format
        assert tuple(fields) == self.tuple._fields

        return True

    def __del__(self):
        self.sock.close()


params = ("left right", 'ff', '224.3.29.71', 10000)

if __name__ == "__main__":
    msg = 'very important data'

    a = Publisher(*params)
    a.send(ip, msg)
