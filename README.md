# UDPComms

This is a simple library to enable communication between different processes (potentially on different machines) over a network using UDP. It's goals a simplicity and easy of understanding. It can send messages to processes running on the same device or to proceses on other devices on the same network (configured using scopes).

Currently it works in python 2 and 3 but it should be relatively simple to extend it to other languages such as C (to run on embeded devices) or Julia (to interface with faster solvers).

The library automatically determines the type of the message and trasmits it along with it, so the subscribers can decode it correctly. While faster to prototype with then systems with explicit type declaration (such as ROS) its easy to shoot yourself in the foot if types are mismatched between publisher and subscriber.

Note that this library doesn't provide any message security. Unless you are using `Scope.Local()` on both ends, not only can anyone on your network evesdrop on messages they can also spoof messages very easily.

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
- `scope` Leave this as the defualt (`Scope.Local()`) to send messages to only this computer. Set to `Scope.Multicast()` to send to others on the network. See Scopes explained for details

### Subscriber Arguments 

- `port`
The port the subscriber will be listen on. 
- `timeout`
If the `recv()` method don't get a message in `timeout` seconds it throws a `UDPComms.timeout` exception
- `scope` Leave this as the defualt (`Scope.All()`) to receive messages from everyone. Set to `Scope.Multicast()` to register that we want to get multicast messages from other devices . See Scopes explained for details


## Scopes Explained

**TLDR** - use `Publisher(port, scope=Scope.Multicast())` and `Subscriber(port, scope=Scope.Multicast())` to get messages to work between different devices

The protocol underlying UDPComms - UDP has a number of differnt [options](https://en.wikipedia.org/wiki/Routing#Delivery_schemes) for how packets can be delivered. By default UDPComms sends messages only to processes on the same device (`Scope.Local()`). To send messages to other computers on the same network use `Scope.Multicast()`. This will default to using the multicast group `239.255.20.22`, but it can be changed by passing an argument. 

Older versions of the library defulted to using a broadcast on the `10.0.0.X` subnet. However, now that the library is often used on differnt networks that is no longer the defualt. To emulate the old behvaiour use `Scope.Broadcast('10.0.0.255')`

Here are all the avalible options:

- `Scope.Local` - Messages meant for this device only 
- `Scope.Multicast`- Messages meant for the specified multicast group
- `Scope.Broadcast` - Messages meant for all devices on this subnet
- `Scope.Unicast` - Publisher only argument that sends messages to a specific ip address only
- `Scope.All` - Subscriber only that listens to packets from all (except for multicast) sources


### Connecting to devices on different networks

If you want to talk to devices aross the internet use [RemoteVPN](https://github.com/stanfordroboticsclub/RemoteVPN) to get them all on the same virtual network and you should be able to use `Scope.Multicast()` from there


## Installation

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

## Extras

### Rover

The library also comes with the `rover` command that can be used to interact with the messages manually.

| Command | Descripion |
|---------|------------|
| `rover peek port` | print messages sent on port `port` |
| `rover poke port rate` | send messages to `port` once every `rate` milliseconds. Type message in json format and press return |

There are more commands used for starting and stoping services described in [this repo](https://github.com/stanfordroboticsclub/RPI-Setup/blob/master/README.md)



### Known issues:

- Macs have issues sending large messages. They are fine receiving them. I think it is related to [this issue](https://github.com/BanTheRewind/Cinder-Asio/issues/9). I wonder does it work on Linux by chance (as the packets happen to be in order) but so far we didn't have issues.

- Messages over the size of one MTU (typically 1500 bytes) will be split up into multiple frames which reduces their chance of getting to their destination on wireless networks.

