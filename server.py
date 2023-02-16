import socket
import protocol
import threading

PORT = 23333
HOST = '127.0.0.1'


def serve(conn, addr):
    with conn:
        while True:
            request = protocol.Message()
            try:
                request.receive_from_socket(conn)
            except Exception as err:
                print(err)
                conn.close()
                break
            
            print("Received from client:", request.op, request.status, request.username, request.message)
            response = protocol.Message()
            response.set_op(request.op)
            response.set_status(0)
            response.set_username(request.username)
            response.set_message("[[[[[[[[" + request.message + "]]]]]]]]")
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
