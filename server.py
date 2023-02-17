import socket
import protocol

import threading
from serverFunction import *

PORT = 23333
HOST = '127.0.0.1'

OPERATION_NOT_SUPPORTED = 100

shared_data = dict()
shared_data['accounts'] = ["example_username"]
shared_data['logged_in_accounts'] = []
shared_data['lock'] = threading.Lock()


def serve(conn, addr):
    current_user = None
    with conn:
        while True:
            request = protocol.Message()
            try:
                request.receive_from_socket(conn)
            except Exception as err:
                print(err)
                conn.close()
                break
            
            print("Received from client:", request.op, request.status, request.username, request.target_name)

            if request.op not in DISPATCH:
                response = protocol.Message()
                response.set_op(request.op)
                response.set_status(OPERATION_NOT_SUPPORTED)
                response.set_message("Operation {} is not supported by the server.".format(request.op))
            else:
                response = DISPATCH[request.op](conn, request, current_user, shared_data)

            try:
                response.send_to_socket(conn)
            except Exception as err:
                print(err)
                conn.close()
                break


if __name__ == "__main__":
    thread_id = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            print('Connected by', addr)
            thread_id += 1
            th = threading.Thread(target=serve, args=(conn, addr))
            th.start()
