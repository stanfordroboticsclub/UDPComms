# UDPComms

This is a simple library to enable communication between different processes (potentially on different machines) over a network using UDP. It's goals a simplicity and easy of understanding. Currently it works in python 2 and 3 but it should be relatively simple to extend it to other languages such as C (to run on embeded devices) or Julia (to interface with faster solvers).

The library automatically determines the type of the message and trasmits it along with it, so the subscribers can decode it correctly. While faster to prototype with then systems with explicit type declaration (such as ROS) its easy to shoot yourself in the foot if types are mismatched between publisher and subscriber.

Note that this library doesn't provide any message security. Not only can anyone on your network evesdrop on messages they can also spoof messages very easily.

## Installation

``` $pip3 install UDPComms ``` :)

Note that if you have an old version of the library installed (before we setup installing via pip) you'll have to uninstll that version manually by removing it from the `site-packages` folder inside your distribution. See this [StackOverflow question](https://stackoverflow.com/questions/402359/how-do-you-uninstall-a-python-package-that-was-installed-using-distutils). Alternativly you could use [virtual environments](https://docs.python.org/3/library/venv.html) to avoid this.

## Usage

### To Send Messages
```
>>> from UDPComms import Publisher
>>> a = Publisher(5500)
>>> a.send({"name":"Bob", "age": 20, "height": 180.5, "mass": 70.1})
```

### To Receive Messages

**TLDR** - you probably want the `get()` method

#### recv Method

Note: before using the `Subsciber.recv()` method read about the `Subsciber.get()` and understand the difference between them. The `Subsciber.recv()` method will pull a message from the socket buffer and it won't necessary be the most recent message. If you are calling it too slowly and there is a lot of messages you will be getting old messages. The `Subsciber.recv()` can also block for up to `timeout` seconds messing up timing.

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

#### get Method
The preferred way of accessing messages is the `Subsciber.get()` method (as opposed to the `recv()` method). It is guaranteed to be nonblocking so it can be used in places without messing with timing. It checks for any new messages and returns the newest one.

If the newest message is older then `timeout` seconds it raises the `UDPComms.timeout` exception. **This is an important safety feature!** Make sure to catch the timeout using `try: ... except UDPComms.timeout: ...` and put the robot in a safe configuration (e.g. turn off motors, when the joystick stop sending messages)

Note that if you call `.get` immediately after creating a subscriber it is possible its hasn't received any messages yet and it will timeout. In general it is better to have a short timeout and gracefully catch timeouts then to have long timeouts

```
>>> from UDPComms import Subscriber, timout
>>> a = Subscriber(5500)
>>> while 1:
>>>     try:
>>>         message = a.get()
>>>         print("got", message)
>>>     except timeout:
>>>         print("safing robot")
```

#### get_list Method
Although UDPComms isn't ideal for commands that need to be processed in order (as the underlying UDP protocol has no guarantees of deliverry) it can be used as such in a pinch. The `Subsciber.get_list()` method will return all the messages we haven't seen yet in a list

```
>>> from UDPComms import Subscriber, timout
>>> a = Subscriber(5500)
>>> messages = a.get_list()
>>> for message in messages:
>>>     print("got", message)
```
-

### Publisher Arguments 
- `port`
The port the messages will be sent on. I recommend keep track of your port numbers somewhere. It's possible that in the future UDPComms will have a system of naming (with a string) as opposed to numbering publishers. 
- `scope` `Scope.LOCAL` will only send messages to only this computer. `Scope.NETWORK` will to send to others on the network. See Scopes explained for details.

### Subscriber Arguments 

- `port`
The port the subscriber will be listen on. 
- `timeout`
If the `recv()` method don't get a message in `timeout` seconds it throws a `UDPComms.timeout` exception
- `scope` There is currently no difference in behaviour between `Scope.LOCAL` and `Scope.NETWORK` - both will receive any messages that get to the device. This is planned to change in the future and `Scope.LOCAL` will only receive local messages.

## Scopes Explained

The protocol underlying UDPComms - UDP has a number of differnt [options](https://en.wikipedia.org/wiki/Routing#Delivery_schemes) for how packets can be delivered. By default UDPComms sends messages only to processes on the same device (`Scope.LOCAL()`). Those are still sent over multicast however the `TTL` (time to live) field is set to 0 so they aren't passed to the network. To send messages to other computers on the same network use `Scope.NETWORK()`. This will default to using the multicast group `239.255.20.22`.

Older versions of the library defaulted to using a broadcast on the `10.0.0.X` subnet. However, now that the library is often used on differnt networks that is no longer the defualt. To emulate the old behvaiour for compatibility use `Scope.BROADCAST`.

Both the multicast group and the broadcast subnet can be changed by overwriting the class varaibles `MULTICAST_IP` and `BROADCAST_IP` respectivly.

Here are all the avalible options:

- `Scope.LOCAL` - Messages meant for this device only 
- `Scope.NETOWORK`- Messages meant for the specified multicast group
- `Scope.BROADCAST ` - Messages meant for all devices on this subnet


### Connecting to devices on different networks

If you want to talk to devices aross the internet use [RemoteVPN](https://github.com/stanfordroboticsclub/RemoteVPN) to get them all on the same virtual network and you should be able to use `Scope.Multicast()` from there


## Extras

### Rover

This repo also comes with the `rover` command that can be used to interact with the messages manually. It doesn't get installed with pip but its here. It depends on the pexpect package you'll have to install manually

| Command | Descripion |
|---------|------------|
| `rover peek port` | print messages sent on port `port` |
| `rover poke port rate` | send messages to `port` once every `rate` milliseconds. Type message in json format and press return |

There are more commands used for starting and stoping services described in [this repo](https://github.com/stanfordroboticsclub/RPI-Setup/blob/master/README.md)



### Known issues:

- Macs have issues sending large messages. They are fine receiving them. I think it is related to [this issue](https://github.com/BanTheRewind/Cinder-Asio/issues/9). I wonder does it work on Linux by chance (as the packets happen to be in order) but so far we didn't have issues.

- Messages over the size of one MTU (typically 1500 bytes) will be split up into multiple frames which reduces their chance of getting to their destination on wireless networks.

