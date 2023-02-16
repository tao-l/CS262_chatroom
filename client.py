import socket
import protocol

HOST = '127.0.0.1'
PORT = 23333

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        request = protocol.ClientMessage()
        request.set_op(23)

        try:
            request.set_username("too_loooooooooooooooong_username")
        except Exception as err:
            print(err)
        
        request.set_username("short_username")
        request.set_message("this is a message.")

        request.send_to_socket(s)
        
        response = protocol.ServerMessage()
        try:
            response.receive_from_socket(s)
        except RuntimeError as err:
            print(err)
        else:
            print("Received from server:", response.op, response.username, response.message)
        
    
        


