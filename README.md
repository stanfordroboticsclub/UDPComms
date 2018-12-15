# UDPComms

This is a simple library to enable communication between different processes (potentially on different machines) over a network using UDP. It's goals a simplicity and easy of understanding and reliability.

Currently it works in python but it should be relatively simple to extend it to C to run on embedded devices like arduino


### To Send Messages
```
>>> from UDPComms import Publisher
>>> a = Publisher("name age height mass", "20sIff", 5500)
>>> a.send("Bob", 20, 180.5, 70.1)
```

### To Receive Messages
```
>>> from UDPComms import Subscriber
>>> a = Subscriber("name age height mass", "20sIff", 5500)
>>> message = a.recv()
>>> message.age
20
>>> message[1]
20
>>> message.height
180.5
>>> message.name
"Bob\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
>>> message
msg(name='Bob\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', age=20, height=180.5, mass=70.0999984741211)
```
Note that string fields maintain the null characters from their C representation. They can be removed using `str.rstrip('\0')`

### Get Method
The preferred way of accessing messages is the `Subsciber.get()` method. It is guarantied to be nonblocking so it can be used in places without messing with timing. It checks for any new messages and returns the newest one.

If the newest message is older then `timeout` seconds it raises the `UDPComms.timeout` exception. This is an important safety feature! Make sure to catch the timeout using `try: ... except UDPComms.timeout: ...` and put the robot in a safe configuration (e.g. turn off motors)

Note that if you call `.get` immediately after creating a subscriber it is possible its hasn't received any messages yet and it will timeout. In general it is better to have a short timeout and gracefully catch timeouts then to have long timeouts

TODO: give examples

### Arguments 

- `fields`
Tuple of human readable names of fields in the message. In addition to recvied messages being able to be indexed by position they can also be accessed using those field names
- `typ`
A struct format string that described the low level message layout. For example the character `'f'` indicated a float while `'20s'` indicates a string of max length 20. You can find more about the format string syntax [here](https://docs.python.org/2/library/struct.html#format-characters)
- `port`
The port the messages will be sent/listed to on. When chosing a port make sure there isn't any conflicts by checking the `UDP Ports` sheet of the [CS Comms System](https://docs.google.com/spreadsheets/d/1pqduUwYa1_sWiObJDrvCCz4Al3pl588ytE4u-Dwa6Pw/edit?usp=sharing) document
- `timeout`
(Subscriber only) If the `recv()` method don't get a message in `timeout` seconds it throws a `UDPComms.timeout` exception
- `local`
(Publisher only) This system will only work if you are connected to the rover subnet (10.0.0.X). If you want to develop with no external hardware (eg raspberry pi) connected set this to True to send packets to localhost instead.


### To Install 

```
$git clone https://github.com/stanfordroboticsclub/UDPComms.git
$sudo bash UDPComms/install.sh
```


