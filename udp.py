import socket
import struct
from collections import namedtuple

class Publisher:
    def __init__(self, fields, typ, multicast_ip, port):
        self.struct = struct.Struct(typ)
        self.tuple = namedtuple("msg", fields)

        assert len(self.tuple._fields) == \
               len(self.struct.unpack( "0"*self.struct.size ))

        self.multicast_group = (multicast_ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.settimeout(0.2)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

        self.sock.connect(self.multicast_group)

    def send(self, *arg, **kwarg):
        msg = self.tuple(*arg, **kwarg)
        data = self.struct.pack(*msg)
        self.sock.send(data)

    def __del__(self):
        self.sock.close()


class Subscriber:
    def __init__(self, fields, typ, multicast_ip, port):
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
        data, address = self.sock.recvfrom(1024)
        print 'received %s bytes from %s' % (len(data), address)
        return self.tuple(*self.struct.unpack(data))

    def __del__(self):
        self.sock.close()


params = ("left right", 'ff', '224.3.29.71', 10000)

if __name__ == "__main__":
    msg = 'very important data'

    a = Publisher(*params)
    a.send(ip, msg)
