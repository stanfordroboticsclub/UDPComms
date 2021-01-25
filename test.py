
from UDPComms import Publisher, Subscriber, Scope, timeout
import time
import subprocess

import unittest

class SingleProcessTestCase(unittest.TestCase):

    def setUp(self):
        self.local_pub = Publisher(8001, scope = Scope.LOCAL )
        self.local_sub = Subscriber(8001, timeout=1, scope = Scope.LOCAL )
        self.local_sub2 = Subscriber(8001, timeout=1, scope = Scope.LOCAL )

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
        self.local_pub = Publisher(8002, scope = Scope.NETWORK )
        self.local_sub = Subscriber(8002, timeout=1, scope = Scope.NETWORK )

    def tearDown(self):
        pass

    def test_simple(self):
        msg = [123, "testing", {"one":2} ] 

        self.local_pub.send( msg )
        recv_msg = self.local_sub.recv()

        self.assertEqual(msg, recv_msg)



class MultiProcessTestCase(unittest.TestCase):

    def setUp(self):
        mirror_server = """(""" \
        """echo "from UDPComms import *";""" \
        """echo "incomming = Subscriber(8003, timeout=5, scope = Scope.NETWORK )";""" \
        """echo "outgoing = Publisher(8000, scope = Scope.NETWORK )";""" \
        """echo "while 1: outgoing.send(incomming.recv())";""" \
        """) | python"""

        self.local_pub = Publisher(8003, scope = Scope.LOCAL )
        self.return_path = Subscriber(8000, timeout = 5, scope = Scope.LOCAL )

        self.p = subprocess.Popen(mirror_server, shell=True, stderr = subprocess.DEVNULL)
        time.sleep(1)# gives enough time to initialize

    def tearDown(self):
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



# socket.gethostbyname('www.google.com')
