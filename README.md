# UDPComms

This is a simple library to enable communication between different processes (potentially on different machines) over a network using UDP. It's goals a simplicity and easy of understanding and reliability.

Currently it works in python but it should be relatively simple to extend it to C to run on embedded devices like arduino


### To Send Messages
```
>>> from UDPComms import Publisher
>>> a = Publisher(5500)
>>> a.send({"name":"Bob", "age": 20, "height": 180.5, "mass": 70.1})
```

### To Receive Messages
```
>>> from UDPComms import Subscriber
>>> a = Subscriber(5500)
>>> message = a.recv()
>>> message['age']
20
>>> message['height']
180.5
>>> message['name']
"Bob"
>>> message
{"name":"Bob", "age": 20, "height": 180.5, "mass": 70.1}
```
This new verison of the library automatically determines the type of the message and trasmits it along with it, so the subscribers can decode it correctly. While faster to prototype with its easy to shoot yourself in the foot if types change unexpectedly.

### Get Method
The preferred way of accessing messages is the `Subsciber.get()` method. It is guarantied to be nonblocking so it can be used in places without messing with timing. It checks for any new messages and returns the newest one.

If the newest message is older then `timeout` seconds it raises the `UDPComms.timeout` exception. **This is an important safety feature!** Make sure to catch the timeout using `try: ... except UDPComms.timeout: ...` and put the robot in a safe configuration (e.g. turn off motors, when the joystick stop sending messages)

Note that if you call `.get` immediately after creating a subscriber it is possible its hasn't received any messages yet and it will timeout. In general it is better to have a short timeout and gracefully catch timeouts then to have long timeouts

TODO: give examples

### Publisher Arguments 
- `port`
The port the messages will be sent on. When chosing a port make sure there isn't any conflicts by checking the `UDP Ports` sheet of the [CS Comms System](https://docs.google.com/spreadsheets/d/1pqduUwYa1_sWiObJDrvCCz4Al3pl588ytE4u-Dwa6Pw/edit?usp=sharing) document
- `local`
This system will only work if you are connected to the rover subnet (10.0.0.X). If you want to develop with no external hardware (eg raspberry pi) connected set this to True to send packets to localhost instead.

### Subscriber Arguments 

- `port`
The port the subscriber will be listen on. 
- `timeout`
If the `recv()` method don't get a message in `timeout` seconds it throws a `UDPComms.timeout` exception

### Rover

The library also comes with the `rover` command that can be used to interact with the messages manually.

TODO docs


### To Install 

```
$git clone https://github.com/stanfordroboticsclub/UDPComms.git
$sudo bash UDPComms/install.sh
```

### To Update 

```
$cd UDPComms
$git pull
$sudo bash install.sh
```


