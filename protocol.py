import struct
import socket

MAX_LENGTH = 20000

# BUFFER = 2      # a very small buffer for testing
BUFFER = 4096     # a large buffer for the actual use      

def receive_n_bytes(s, n):
    """ receives exactly n bytes from socket s
        Raise RuntimeError if socket conection broken  """
    bin = b''
    received = 0
    while received < n:
        chunk = s.recv(min(n - received, BUFFER))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        bin += chunk
        received += len(chunk)
    return bin


class Message:
    #  op, username, message must be set by the set methods to ensure validity. 
    def __init__(self, op=0, status=0, username="", message=""):
        self.set_op(op)
        self.set_status(status)
        self.set_username(username)
        self.set_message(message)
    
    def set_op(self, op):
        self.op = op
    
    def set_status(self, status):
        self.status = status
    
    def set_username(self, username):
        self.username = username
    
    def set_message(self, message):
        self.message = message

    def encode(self):
        """ Encode the object into a binary string
            Raise errors if the object cannot be encoded """
        binary = struct.pack('!H', self.op)
        binary += struct.pack('!H', self.status)
        username_binary = self.username.encode("utf-8")
        binary += struct.pack('!H', len(username_binary))
        binary += username_binary
        message_binary = self.message.encode("utf-8")
        binary += struct.pack('!H', len(message_binary))
        binary += message_binary
        return binary
    
    def decode_from(self, binary):
        """ construct the objection from a binary string
            Raise errors if the binary string cannot be decoded """
        self.set_op( struct.unpack('!H', binary[:2])[0] )
        parsed = 2
        self.set_status( struct.unpack('!H', binary[2:4])[0] )
        parsed = 4 
        username_len = struct.unpack('!H', binary[parsed : parsed+2])[0]
        parsed += 2
        self.set_username( binary[parsed : parsed+username_len].decode("utf-8") )
        parsed += username_len
        message_len = struct.unpack('!H', binary[parsed : parsed+2])[0]
        parsed += 2
        self.set_message( binary[parsed : parsed+message_len].decode("utf-8") )
        parsed += message_len

        l = len(binary)
        if parsed != l:
            raise ValueError('Parsed length {} != binary length {}'.format(parsed, l))


    def send_to_socket(self, s):
        """ Raise error if sending fails """
        binary = self.encode()
        length = len(binary)
        to_send = struct.pack('!H', length) + binary
        s.sendall( to_send )

    def receive_from_socket(self, s):
        """ Raise error if receiving fails """
        bin = receive_n_bytes(s, 2)
        length = struct.unpack('!H', bin)[0]
        if length > MAX_LENGTH:
            raise ValueError("Received message length {} is too long".format(length))
        bin = receive_n_bytes(s, length)
        self.decode_from(bin)
