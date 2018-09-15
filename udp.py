import socket
import struct


# class Publisher:
#     def __init__(self, typ, multicast, port

def send(multicast_group, message):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    sock.settimeout(0.2)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

    sent = sock.sendto(message, multicast_group)
    sock.close()


def recv(ip):
    multicast_group = ip[0]
    server_address = ('', ip[1])

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind to the server address
    sock.bind(server_address)


    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    data, address = sock.recvfrom(1024)
    print 'received %s bytes from %s' % (len(data), address)
    return data

ip = ('224.3.29.71', 10000)

if __name__ == "__main__":
    msg = 'very important data'
    ip = ('224.3.29.71', 10000)
    send(ip, msg)
