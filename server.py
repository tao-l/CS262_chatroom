import socket
import threading
import sys

import protocol
from serverFunction import *

PORT = 23333

def serve(conn, addr):
    with conn:
        request = protocol.Message()
        try:
            request.receive_from_socket(conn)
        except Exception as err:
            print(err)
            conn.close()
            return
        
        print("Received from client:", request.op, request.status, request.username, request.target_name)

        if request.op not in DISPATCH:
            response = protocol.Message()
            response.set_op(request.op)
            response.set_status(protocol.OPERATION_NOT_SUPPORTED)
            response.set_message(f"Operation {request.op} is not supported by the server.")
            response_list = [ response ]
        else:
            response_list = DISPATCH[request.op](request)

        try:
            for response in response_list: 
                response.send_to_socket(conn)
            print("Responses sent succesfully to", addr)
        except Exception as err:
            print(err)
            conn.close()


if __name__ == "__main__":
    mode = "local"

    if len(sys.argv) == 2:
        if sys.argv[1].lower() ==  "network":
            mode = "network"
    
    if mode == "local":
        # Local mode:   set the HOST to be 127.0.0.1
        HOST = "127.0.0.1"
        print("Local mode. \n  Client should connect to", HOST)
    else:
        # Network mode:   get the IP address of the server and print it.   
        HOST = "0.0.0.0"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_addr = s.getsockname()[0]
        print("Network mode. \n  Server's IP address:", ip_addr) 
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(128)
        print("  Listening at port:", PORT)
        while True:
            conn, addr = s.accept()
            print('\nConnected by', addr)
            conn.settimeout(300)
            # conn.settimeout(5)      # a small timeout is used when testing. 
            th = threading.Thread(target=serve, args=(conn, addr))
            th.start()
