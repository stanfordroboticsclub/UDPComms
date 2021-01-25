
from UDPComms import Publisher, Subscriber, Scope, timeout
import time

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



if __name__ == "__main__":
    unittest.main()



# socket.gethostbyname('www.google.com')
