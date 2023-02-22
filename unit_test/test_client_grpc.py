import grpc
import service_pb2 as pb2
import service_pb2_grpc
import sys
sys.path.append('..')
from gRPC.serverFunction import *
from serverFunction import *

HOST = '127.0.0.1'
PORT = 23333

def create_stub():
    channel = grpc.insecure_channel(HOST+":"+PORT)
    stub = service_pb2_grpc.ChatRoomStub(channel)
    return stub

def test_create_account():
    stub = create_stub()
    user = pb2.User(username="gary")
    response = stub.rpc_create_account(user)
    print(response.message)
    assert response.status == SUCCESS

    user = pb2.User(username="gary")
    response = stub.rpc_create_account(user)
    print(response.message)
    assert response.status == GENERAL_ERROR

    user = pb2.User(username="gary2")
    response = stub.rpc_create_account(user)
    print(response.message)
    assert response.status == SUCCESS

    
def test_check_account():
    stub = create_stub()
    user = pb2.User(username="gary")
    response = stub.rpc_check_account(user)
    print(response.message)
    assert response.status == SUCCESS

    user = pb2.User(username="ft")
    response = stub.rpc_check_account(user)
    print(response.message)
    assert response.status == ACCOUNT_NOT_EXIST


def test_list_account():
    stub = create_stub()
    wildcard = pb2.Wildcard("ga")
    for user in stub.rpc_list_account(wildcard):
        print(user.username) # nothhing should print here

    wildcard = pb2.Wildcard("ga*")
    for user in stub.rpc_list_account(wildcard):
        print(user.username) # should print gary

    wildcard = pb2.Wildcard("*")
    for user in stub.rpc_list_account(wildcard):
        print(user.username) # should print gary and gary2


def test_send_message():
    stub = create_stub()
    chat_msg = pb2.ChatMessage(username="gary",target_name="gary",message="A first message.")
    response = stub.rpc_send_message(chat_msg)
    print(response.message)
    assert response.status == SUCCESS

    chat_msg = pb2.ChatMessage(username="gary1",target_name="gary2",message="None existing from")
    response = stub.rpc_send_message(chat_msg)
    print(response.message)
    assert response.status == ACCOUNT_NOT_EXIST

    chat_msg = pb2.ChatMessage(username="gary",target_name="gary3",message="None existing to")
    response = stub.rpc_send_message(chat_msg)
    print(response.message)
    assert response.status == ACCOUNT_NOT_EXIST

    chat_msg = pb2.ChatMessage(username="gary2",target_name="gary",message="A second message.")
    response = stub.rpc_send_message(chat_msg)
    print(response.message)
    assert response.status == SUCCESS

    chat_msg = pb2.ChatMessage(username="gary",target_name="gary2",message="gary2's new message.")
    response = stub.rpc_send_message(chat_msg)
    print(response.message)
    assert response.status == SUCCESS
    

def test_fetch_message():
    stub = create_stub()
    fetch_request = pb2.FetchRequest(msg_id=1,username="gary")
    for chat_msgs in stub.rpc_fetch_message(fetch_request):
        print(chat_msgs.message) # this should print A first message and A second message

    fetch_request = pb2.FetchRequest(msg_id=0,username="gary")
    for chat_msgs in stub.rpc_fetch_message(fetch_request):
        print(chat_msgs.message) # this should print message id<1

    fetch_request = pb2.FetchRequest(msg_id=3,username="gary")
    for chat_msgs in stub.rpc_fetch_message(fetch_request):
        print(chat_msgs.message) # this should print message id > total number of messages
    

def test_delete_account():
    stub = create_account()

    user = pb2.User("gary2")
    response = stub.rpc_check_account(user)
    assert response.status == SUCCESS
    assert response.message == "Account exists."

    user = pb2.User("gary2")
    response = stub.rpc_delete_account(user)
    print(response.message)
    assert response.status == SUCCESS

    response = stub.rpc_check_account(user)
    assert response.status == ACCOUNT_NOT_EXIST
    assert response.message == "Account does not exist."

    user = pb2.User("gary3")
    response = stub.rpc_delete_account(user)
    print(response.message)
    assert response.status == ACCOUNT_NOT_EXIST

     

if __name__ == "__main__":

    test_create_account()
    test_check_account()
    test_list_account()
    test_send_message()
    test_fetch_message()
    test_delete_account()

