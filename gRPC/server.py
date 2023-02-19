from concurrent import futures
import logging

import grpc
import service_pb2_grpc
import serverFunction


PORT = 23333

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=128))
    service_pb2_grpc.add_ChatRoomServicer_to_server(
        serverFunction.ChatRoomServicer(),
        server
    )
    server.add_insecure_port("[::]:2333")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
