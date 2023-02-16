import socket
import protocol
import threading

PORT = 23333
HOST = '127.0.0.1'

class ServerThread(threading.Thread):
    def __init__(self, thread_id, conn, addr):
        threading.Thread.__init__(self)
        self.id = thread_id
        self.conn = conn
        self.addr = addr

    def run(self):
        while True:
            request = protocol.ClientMessage()
            try:
                request.receive_from_socket(conn)
            except Exception as err:
                print(err)
                conn.close()
                break
            
            print("Received from client:", request.op, request.username, request.message)
            response = protocol.ServerMessage()
            response.set_op(request.op)
            response.set_username(request.username)
            response.set_message("[[[[[[[[" + request.message + "]]]]]]]]")
            response.send_to_socket(conn)

        print("Thread {} ends".format(self.id))


if __name__ == "__main__":
    thread_id = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            print('Connected by', addr)
            thread_id += 1
            th = ServerThread(thread_id, conn, addr)
            th.start()
