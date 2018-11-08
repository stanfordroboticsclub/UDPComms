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
Note that string fields maintain the null characters from their C representation. THye can be removed using `str.rstrip('\0')`

### Arguments 

- `fields`
Tuple of human readable names of fields in the message. In addition to recvied messages being able to be indexed by position they can also be accessed using those field names
- `typ`
A struct format string that described the low level message layout. For example the character `'f'` indicated a float while `'20s'` indicates a string of max length 20. You can find more about the format string syntax [here](https://docs.python.org/2/library/struct.html#format-characters)
- `port`
The port the messages will be sent/listed to on. When chosing a port make sure there isn't any conflicts by checking the `UDP Ports` sheet of the [CS Comms System](https://docs.google.com/spreadsheets/d/1pqduUwYa1_sWiObJDrvCCz4Al3pl588ytE4u-Dwa6Pw/edit?usp=sharing) document
- `timeout`
(Subscriber only) If the `recv()` method don't get a message in `timeout` seconds it throws a `UDPComms.timeout` exception


### To Install 

```
$git clone https://github.com/stanfordroboticsclub/UDPComms.git
$sudo ./UDPComms/install.sh
```


### Changing the broadcast address

Currently the broadcast address is set to "10.0.0.255" which will send messages to all nodes on the rover subnet (10.0.0.X). To change this address change `Publisher.broadcast_ip`. Sometime this is necessary if you are trying to test some code without a connection to the rover subnet (ie no external hardware). To over come this set `Publisher.broadcast_ip = "<broadcast>"` 


