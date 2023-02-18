import socket
import threading
import time
import random
import sys
sys.path.append('../')
from protocol import *

HOST = '127.0.0.1'
PORT = 23333

#### helpful subroutines
def create_an_account(username, show):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = Message(CREATE_ACCOUNT, 0, username)
        if show:
            print(f"Request to create account [{username}]")
        request.send_to_socket(s)
        if show:
            response = Message()
            response.receive_from_socket(s)
            print("Response:", response.status, response.message)

def delete_an_account(username, show):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = Message(DELETE_ACCOUNT, 0, username)
        if show:
            print(f'Request to delete account [{username}]')
        request.send_to_socket(s)
        if show:
            response = Message()
            response.receive_from_socket(s)
            print("Response:", response.status, response.message)

def send_message(username, target_name, message, show):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = Message(SEND_MESSAGE, 0, username, target_name, message)
        if show:
            print(f'Request to send message: [{username}]  --> [{target_name}]')
        request.send_to_socket(s)
        if show:
            response = Message()
            response.receive_from_socket(s)
            print("Response:", response.status, response.message)

def fetch_message(username, msg_id, show):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = Message(FETCH_MESSAGE, msg_id, username)
        if show:
            print(f'Request to fetch message: [{username}], msg_id=[{msg_id}]')
        request.send_to_socket(s)
        response = Message()
        response.receive_from_socket(s)
        if show:    
            print("Response:  status =", response.status)
            print("  ", response.username, ":", response.message)
    return response

def fetch_all(username):
    print(f"Fetch all messages for [{username}]:")
    msg_id = 1
    while True:
        response = fetch_message(username, msg_id, show=False)
        if response.status == MESSAGE_ID_TOO_LARGE:
            break
        assert response.status in (NO_NEXT_MESSAGE, NEXT_MESSAGE_EXIST)
        print("  ", response.username, ":", response.message)
        if response.status == NO_NEXT_MESSAGE:
            break
        msg_id += 1

##### Testing functions
def test__create_list_check_delete__account():
    print("\n=================== BEGIN: testing create, list, check, delete =================")

    print("Testing creating an account with a very long (invalid) username.")
    create_an_account("a very very long username (which is invalid).", show=True)
    
    print("\n----------------------------------")
    print("Testing creating an account twice.")
    create_an_account("CS262", show=True)
    create_an_account("CS262", show=True)
    

    print("\n----------------------------------")
    print("Testing creating a lot of accounts simultaneously.")

    N = 110
    

    threads = []
    for i in range(N):
        username = f'user_{i}'
        th = threading.Thread(target=create_an_account, args=(username, False))
        threads.append(th)
        th.start()
    

    print("\n----------------------------------")
    print("Testing listing accounts:")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = Message(LIST_ACCOUNT)
        request.set_message("user*")
        request.send_to_socket(s)
        response = Message()
        response.receive_from_socket(s)
        print("Accounts:")
        print(response.message)
    
    for th in threads:
        th.join()
    
    print("\n----------------------------------")
    print("Count how many accounts are actually created.  (testing check_account)")
    cnt = 0
    for i in range(N + 10):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            request = Message(CHECK_ACCOUNT)
            request.set_username(f"user_{i}")
            request.send_to_socket(s)
            response = Message()
            response.receive_from_socket(s)
            if response.status == SUCCESS:
                cnt += 1
            else:
                assert response.status == ACCOUNT_NOT_EXIST
    print(f"Expected: {N},   actually: {cnt},    good!")


    print("\n----------------------------------")
    print("Testing deleting accounts:")
    print("Delete non-existing accounts: ")
    delete_an_account("no such account", show=True)
    
    print("\nDeleting a lot of accounts simultaneously: ")
    threads = []
    for i in range(N - 10):
        username = f'user_{i}'
        th_1 = threading.Thread(target=delete_an_account, args=(username, False))
        threads.append(th_1)
        th_1.start()
        # repeat deleting this account.  Should not affect the result. 
        th_2 = threading.Thread(target=delete_an_account, args=(username, False))
        threads.append(th_2)
        th_2.start()
    for th in threads:
        th.join()
    
    print("List the remaining accounts:")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = Message(LIST_ACCOUNT)
        request.set_message("*")
        request.send_to_socket(s)
        response = Message()
        response.receive_from_socket(s)
        print(response.message)
    print("We should only see 10 accounts with name [user_XXX].   Good!")


    print("\n=================== END: testing create, list, check, delete =================\n")


def test__send_fetch__message():
    print("\n=================== BEGIN: testing send, fetch messages ==================")

    print("Creating two accounts")
    create_an_account("Alice", show=True)
    create_an_account("Bob", show=True)

    print("\nBad sendins:")
    send_message("Alice", "no such user", "message", show=True)
    send_message("no such user", "Bob", "message", show=True)
    send_message("Alice", "Bob", "m"*(MESSAGE_LIMIT+1), show=True)
    
    print("\nGood sendings:")
    send_message("Alice", "Bob", "A to B message", show=True)
    send_message("Bob", "Alice", "B to A message", show=True)
    send_message("Alice", "Alice", "A to A message", show=True)
    send_message("Bob", "Bob", "B to B message", show=True)

    print("\nGood fetches:")
    fetch_message("Alice", 1, show=True)
    fetch_message("Alice", 2, show=True)
    fetch_message("Bob", 2, show=True)

    print("\nBad fetches:")
    fetch_message("no such user", 1, show=True)
    fetch_message("Bob", 3, show=True)
    fetch_message("Alice", 0, show=True)
    fetch_message("Bob", -1, show=True)

    print("\nDelete account and then fetch:")
    delete_an_account("Bob", show=True)
    fetch_message("Bob", 1, show=True)

    print("\nRe-create an account and then fetch:")
    create_an_account("Bob", show=True)
    fetch_message("Bob", 1, show=True)
    print("Should say msg_id > total number of mesages 0.   Good!")


    print("\nRe-creation of [Bob] should not affect [Alice]'s messages received from [Bob] previously:")
    fetch_all("Alice")
    fetch_all("Bob")

    print("\n=================== END: testing send, fetch messages ==================")

if __name__ == "__main__":

    # test__create_list_check_delete__account()

    test__send_fetch__message()

