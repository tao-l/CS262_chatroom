import logging

import grpc
import service_pb2
import service_pb2_grpc


USERNAME_LIMIT = 20
MESSAGE_LIMIT = 500


SUCCESS = 0

 # error codes: range in [100, 199]
INVALID_USERNAME = 101
ACCOUNT_NOT_EXIST = 102
MESSAGE_TOO_LONG = 103
MESSAGE_ID_TOO_LARGE = 104
GENERAL_ERROR = 199


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:2333') as channel:
        stub = service_pb2_grpc.ChatRoomStub(channel)

        print("------ Creating account: invalid ------")
        user = service_pb2.User(username="a very very long username (which is invalid)")
        response = stub.rpc_create_account(user)
        print(response.status, response.message)

        print("------ Creating account: good ------")
        user = service_pb2.User(username="short username")
        response = stub.rpc_create_account(user)
        print(response.status, response.message)


if __name__ == "__main__":
    logging.basicConfig()
    run()