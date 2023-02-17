import struct
import socket

MAX_OP = 32767
USERNAME_LIMIT = 20
MESSAGE_LIMIT = 500

BUFFER = 2      # a very small buffer for testing

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


class ClientMessage:
    #  op, username, message must be set by the set methods to ensure validity. 
    def __init__(self, op=0, username="", message=""):
        self.set_op(op)
        self.set_username(username)
        self.set_message(message)
    
    def set_op(self, op):
        if op < 0  or  op > MAX_OP:
            raise ValueError("operation code {} out of range [0, {}]".format(op, MAX_OP))
        self.op = op
    
    def set_username(self, username):
        if len(username) > USERNAME_LIMIT:
            raise ValueError("Username longer than {}.".format(USERNAME_LIMIT))
        self.username = username
    
    def set_message(self, message):
        if len(message) > MESSAGE_LIMIT:
            raise ValueError("Message longer than {}.".format(MESSAGE_LIMIT))
        self.message = message

    def encode(self):
        """ Encode the object into a binary string
            Raise errors if the object cannot be encoded """
        binary = struct.pack('!H', self.op)
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
        """ Raise exception if """
        binary = self.encode()
        length = len(binary)
        to_send = struct.pack('!H', length) + binary
        s.sendall( to_send )

    def receive_from_socket(self, s):
        """ Raise RuntimeError if socket connection broken """
        bin = receive_n_bytes(s, 2)
        length = struct.unpack('!H', bin)[0]
        bin = receive_n_bytes(s, length)
        self.decode_from(bin)


ServerMessage = ClientMessage 


####################  The following codes are for testing only  #################### 
def test():
    obj = ClientMessage()
    try:
        obj.set_op(MAX_OP + 1)
    except Exception as err:
        print(err)
    try:
        obj.set_username("asdafljsadlfkjas;dlfkjasdlkfjasldkfj")
    except Exception as err:
        print(err)
    try:
        obj.set_message("a" * MESSAGE_LIMIT + 'b')
    except Exception as err:
        print(err)
    
    obj = ClientMessage(2, "user_name", "    this\tis\ta\message.")

    bin = obj.encode()
    print(bin)
    aha = ClientMessage()
    aha.decode_from(bin)
    print(aha.op, aha.username, aha.message)

    bin_2 = bin + b'extra text'
    try:
        aha.decode_from(bin_2)
    except Exception as err:
        print(err)
    
    bin_3 = bin[0 : len(bin)-3]
    try:
        aha.decode_from(bin_3)
    except Exception as err:
        print(err)

if __name__ == "__main__":
    test()
