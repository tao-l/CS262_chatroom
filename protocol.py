import struct
import socket

CREATE_ACCOUNT = 1
CHECK_ACCOUNT = 2
LIST_ACCOUNT = 3
DELETE_ACCOUNT = 4
SEND_MESSAGE = 5
FETCH_MESSAGE = 6


USERNAME_LIMIT = 20
MESSAGE_LIMIT = 500


SUCCESS = 0
NO_NEXT_MESSAGE = 1
NEXT_MESSAGE_EXIST = 2


 # error codes are from [100, 199]
OPERATION_NOT_SUPPORTED = 100
INVALID_USERNAME = 101
ACCOUNT_NOT_EXIST = 102
MESSAGE_TOO_LONG = 103
MESSAGE_ID_TOO_LARGE = 104
GENERAL_ERROR = 199



PROTOCOL_MAX_LEN = 20000

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
    """ Define a message object that can be sent and received via socket. 
        This message object is used in both of the client's request and the server's response.
        - It has 4 attributes:
                op, status, username, target_name, message
        - To send a message object [msg] to a socket, call the method:
                msg.send_to_socket(s)
          The object is encoded by the encode() function before sending. 
        - To receive a message object [msg] from a socket, call the method:
                msg = Message()
                msg.receive_from_socket(s)
          The object is obtained by decoding the binary string received from socket. 
    """
    def __init__(self, op=0, status=0, username="", target_name="", message=""):
        self.set_op(op)
        self.set_status(status)
        self.set_username(username)
        self.set_target_name(target_name)
        self.set_message(message)
    
    def set_op(self, op):
        self.op = op
    
    def set_status(self, status):
        self.status = status
    
    def set_username(self, username):
        self.username = username
    
    def set_target_name(self, target_name):
        self.target_name = target_name
    
    def set_message(self, message):
        self.message = message

    def encode(self):
        """ Encode the message object into a binary string
            Raise errors if the object cannot be encoded """
        binary = struct.pack('!h', self.op)

        binary += struct.pack('!i', self.status)

        username_binary = self.username.encode("utf-8")
        binary += struct.pack('!H', len(username_binary))
        binary += username_binary

        target_name_binary = self.target_name.encode("utf-8")
        binary += struct.pack('!H', len(target_name_binary))
        binary += target_name_binary
        
        message_binary = self.message.encode("utf-8")
        binary += struct.pack('!H', len(message_binary))
        binary += message_binary

        return binary
    
    def decode_from(self, binary):
        """ construct the message object from a binary string
            Raise errors if the binary string cannot be decoded """
        self.set_op( struct.unpack('!h', binary[:2])[0] )
        parsed = 2

        self.set_status( struct.unpack('!i', binary[parsed:parsed+4])[0] )
        parsed += 4 

        username_len = struct.unpack('!H', binary[parsed : parsed+2])[0]
        parsed += 2
        if username_len > PROTOCOL_MAX_LEN:
            raise ValueError("Username too long!")
        self.set_username( binary[parsed : parsed+username_len].decode("utf-8") )
        parsed += username_len

        target_name_len = struct.unpack('!H', binary[parsed : parsed+2])[0]
        parsed += 2
        if target_name_len > PROTOCOL_MAX_LEN:
            raise ValueError("Taget username too long!")
        self.set_target_name( binary[parsed : parsed+target_name_len].decode("utf-8") )
        parsed += target_name_len

        message_len = struct.unpack('!H', binary[parsed : parsed+2])[0]
        parsed += 2
        if message_len > PROTOCOL_MAX_LEN:
            raise ValueError("Message too long!")
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
        if length > PROTOCOL_MAX_LEN:
            raise ValueError("Received message length {} is too long".format(length))
        bin = receive_n_bytes(s, length)
        self.decode_from(bin)


####################### Testing code #####################
def test():
    msg = Message(1, 2147483647, "username", "target_name", "this is\ta message")
    bin = msg.encode()
    msg_2 = Message()
    msg_2.decode_from(bin)
    print(msg_2.op, msg_2.status, msg_2.username, msg_2.target_name)
    print("     ", msg_2.message)

    try:
        msg.set_target_name("sb"*PROTOCOL_MAX_LEN)
        bin = msg.encode()
        msg_2.decode_from(bin)
        print(msg_2.op, msg_2.status, msg_2.username, msg_2.target_name)
        print("     ", msg_2.message)
    except Exception as err:
        print(err)

if __name__ == "__main__":
    test()