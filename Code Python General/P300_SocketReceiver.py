import socket

class P300_SocketReceiver(object):
    
    def __init__(self, controller, HOST, PORT, BUFFER_SIZE = 1024):
        
        self.controller = controller
        self.HOST = HOST
        self.PORT = PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        
        # Socket Establishment
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect
        self.connect()
    
    def __del__(self):
        self.disconnect()
        del self
        
    def connect(self):
        self.socket.connect((self.HOST, self.PORT))
        self.socket.send(b'\r\n')
    
    def disconnect(self):
        self.socket.close()
    
    def receive(self):
        return self.socket.recv(self.BUFFER_SIZE)
    
    def setblocking(self, flag):
        self.socket.setblocking(flag)