from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

class ClientChannel(Channel):

    def Network(data):
        print(data)

    def Network_myaction(data):
        print("myaction", data)

        # e.g. data = {"action": "myaction", "blah": 123, ...}

class MyServer(Server):
    
    channelClass = ClientChannel

    def Connected(self, channel, addr):
        print("new connection:", channel)

myserver = MyServer()
while True:
    myserver.Pump()
    sleep(0.0001)
