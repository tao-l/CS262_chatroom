import socket
import threading

import protocol
from serverFunction import *

PORT = 23333
HOST = '127.0.0.1'


class SharedData():
    def __init__(self):
        self.accounts = ["example_username"]
        self.lock = threading.Lock()

shared_data = SharedData()

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
        else:
            response = DISPATCH[request.op](request, shared_data)

        try:
            response.send_to_socket(conn)
            print("Response sent succesfully")
        except Exception as err:
            print(err)
            conn.close()


if __name__ == "__main__":
    thread_id = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            print('\nConnected by', addr)
            th = threading.Thread(target=serve, args=(conn, addr))
            th.start()
