
from UDPComms import Publisher, Subscriber, timeout
import time
import subprocess
import os
import socket

import unittest

class SingleProcessTestCase(unittest.TestCase):

    def setUp(self):
        self.local_pub = Publisher(8001, target = '127.0.0.1' )
        self.local_sub = Subscriber(8001, timeout=1, target = '127.0.0.1' )
        self.local_sub2 = Subscriber(8001, timeout=1, target = '127.0.0.1' )

    def tearDown(self):
        pass

    def test_simple(self):
        msg = [123, "testing", {"one":2} ] 

        self.local_pub.send( msg )
        recv_msg = self.local_sub.recv()

        self.assertEqual(msg, recv_msg)

    def test_bytes(self):
        msg = ["testing", b"bytes"] 

        self.local_pub.send( msg )
        recv_msg = self.local_sub.recv()

        self.assertEqual(msg, recv_msg)

    def test_dual_recv(self):
        msg = [124, "testing", {"one":3} ] 

        self.local_pub.send( msg )
        recv_msg = self.local_sub.recv()
        recv_msg2 = self.local_sub2.recv()

        self.assertEqual(msg, recv_msg)
        self.assertEqual(msg, recv_msg2)

    def test_get_recv(self):
        msg = [123, "testing", {"one":2} ] 

        self.local_pub.send( msg )
        time.sleep(0.1)

        self.assertEqual(msg, self.local_sub.get())
        self.assertEqual(msg, self.local_sub.get())

        msg2 = "hello"
        self.local_pub.send( msg2 )
        time.sleep(0.1)
        self.assertEqual(msg2, self.local_sub.get())

        time.sleep(1)

        with self.assertRaises(timeout):
            self.local_sub.get()

class SingleProcessNetworkTestCase(unittest.TestCase):

    def setUp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 1)) #gets ip of default interface
            network_ip_address = s.getsockname()[0]

        self.pub = Publisher(8002, target = network_ip_address ) 
        self.sub = Subscriber(8002, timeout=1, target = network_ip_address ) 
        self.sub2 = Subscriber(8002, timeout=1, target = network_ip_address ) 

    def tearDown(self):
        pass

    def test_simple(self):
        msg = [123, "testing", {"one":2} ] 

        self.pub.send( msg )
        recv_msg = self.sub.recv()

        self.assertEqual(msg, recv_msg)

    def test_dual_recv(self):
        msg = [125, "testing", {"one":3} ] 

        self.pub.send( msg )
        recv_msg = self.sub.recv()
        recv_msg2 = self.sub2.recv()

        self.assertEqual(msg, recv_msg)
        self.assertEqual(msg, recv_msg2)

class MixTargetsTestCase(unittest.TestCase):

    def setUp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 1)) #gets ip of default interface
            network_ip_address = s.getsockname()[0]

        self.pub_net = Publisher(8005, target = network_ip_address ) 
        self.pub_local = Publisher(8005, target = "127.0.0.1" ) 

        self.sub_local = Subscriber(8005, timeout=1, target = "127.0.0.1" ) 
        self.sub_net = Subscriber(8005, timeout=1, target = network_ip_address ) 
        self.sub_all = Subscriber(8005, timeout=1, target = "0.0.0.0" ) 

    def tearDown(self):
        pass

    def test_local_send(self):
        msg = [123, "local", {"one":2.2} ] 

        self.pub_local.send( msg )

        self.assertEqual(msg, self.sub_all.recv())
        self.assertEqual(msg, self.sub_local.recv())
        self.assertRaises(timeout, self.sub_net.recv)

    def test_net_send(self):
        msg = [123, "net", {"one":2.3} ] 

        self.pub_net.send( msg )

        self.assertEqual(msg, self.sub_all.recv())
        self.assertEqual(msg, self.sub_net.recv())
        self.assertRaises(timeout, self.sub_local.recv)


class MultiProcessTestCase(unittest.TestCase):

    def setUp(self):
        mirror_server = b"""
from UDPComms import *;
import sys
incomming = Subscriber(8003, timeout=10);
outgoing = Publisher(8000);
print("ready");
sys.stdout.flush()
while 1: outgoing.send(incomming.recv());

"""

        self.p = subprocess.Popen('python3', stdin = subprocess.PIPE, stdout=subprocess.PIPE)
        self.p.stdin.write(mirror_server)
        self.p.stdin.close()
        self.p.stdout.readline() #wait for program to be ready

        self.local_pub = Publisher(8003)
        self.return_path = Subscriber(8000, timeout = 5)

    def tearDown(self):
        self.p.stdout.close()
        self.p.terminate()
        self.p.wait()

    def test_simple(self):
        msg = [123, "testing", {"one":2} ] 

        self.local_pub.send( msg )
        self.assertEqual(msg, self.return_path.recv())

        msg2 = "hi"
        self.local_pub.send(msg2)
        self.assertEqual(msg2, self.return_path.recv())

if __name__ == "__main__":
    unittest.main()


