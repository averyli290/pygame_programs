from PodSixNet.Connection import connection

connection.Connect()

connection.Send({"action": "test"})

class Client(ConnectionListener):
    def __init__(self, host, port):
        self.Connnect((host, port))
        connection.send({"action": "nickname", "nickname": "test0"})

        t = start_new_thread(self.InputLoop, ())

    def InputLoop():
        while 1:
            connection.send({"action": "message", "message": stdin.readline().rstrip("\n")})
    


while True:
    connection.pump()
