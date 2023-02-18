import socket
import threading
import time
import random
import sys
sys.path.append('../')
from protocol import *

HOST = '127.0.0.1'
PORT = 23333


def test__create_list_check_deleta__account():
    print("\n===================== BEGIN: testing create, list, check, delete ===================")

    print("Testing creating an account with a very long (invalid) username.")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = Message(CREATE_ACCOUNT, 0)
        request.set_username("a_very_long_username_which_is_invalid")
        request.send_to_socket(s)
        response = Message()
        response.receive_from_socket(s)
        print("Error message: ", response.status, response.message)
    
    print("\n----------------------------------")
    print("Testing creating an account twice.")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = Message(CREATE_ACCOUNT, 0, "CS262")
        request.send_to_socket(s)
        response = Message()
        response.receive_from_socket(s)
        print("Success message: ", response.status, response.message)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request.send_to_socket(s)
        response.receive_from_socket(s)
        print("Error message: ", response.status, response.message)
    

    print("\n----------------------------------")
    print("Testing creating a lot of accounts simultaneously.")

    N = 200
    
    def create_one_account(id):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            request = Message(CREATE_ACCOUNT, 0, f"user_{id}")
            request.send_to_socket(s)
    threads = []
    for i in range(N):
        th = threading.Thread(target=create_one_account, args=(i, ))
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
    print("Delete non-existing accounts; ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = Message(DELETE_ACCOUNT)
        request.set_username("no such account")
        request.send_to_socket(s)
        response = Message()
        response.receive_from_socket(s)
        print(response.message)
    
    print("\nDeleting a lot of accounts simultaneously: ")
    def delete_one_account(id):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            request = Message(DELETE_ACCOUNT, 0, f"user_{id}")
            request.send_to_socket(s)
    threads = []
    for i in range(N - 10):
        th_1 = threading.Thread(target=delete_one_account, args=(i, ))
        threads.append(th_1)
        th_1.start()
        # repeat deleting this account.  Should not affect the result. 
        th_2 = threading.Thread(target=delete_one_account, args=(i, ))
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


    print("\n===================== END: testing create, list, check, delete ===================\n")


    
if __name__ == "__main__":

    test__create_list_check_deleta__account()

    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    #     request = Message(CREATE_ACCOUNT, 0, "test_user_1", "target_user_name")
    #     request.send_to_socket(s)
    #     response = Message()
    #     response.receive_from_socket(s)

    #     print("Reponse 3:", response.status, response.message)
    
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    #     request = Message(CREATE_ACCOUNT, 0, "test_user_2", "target_user_name_2")
    #     request.send_to_socket(s)
    #     response.receive_from_socket(s)

    #     print("Reponse 4:", response.status, response.message)
    
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    #     request = Message(CREATE_ACCOUNT, 0, "test_user_1", "")
    #     request.send_to_socket(s)
    #     response.receive_from_socket(s)

    #     print("Reponse 5:", response.status, response.message)
    
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    #     request = Message()
    #     request.set_op(LIST_ACCOUNT)
    #     request.set_message("test*")
    #     request.send_to_socket(s)
        
    #     response = Message()
    #     try:
    #         response.receive_from_socket(s)
    #     except Exception as err:
    #         print(err)
    #     else:
    #         print("Response 6:\n Received from server: ", response.op, response.status, response.username)
    #         print("message: ")
    #         print(response.message)
    
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    #     request = Message()
    #     request.set_op(CHECK_ACCOUNT)
    #     request.set_username("not existing username")
    #     request.send_to_socket(s)
        
    #     response = Message()
    #     response.receive_from_socket(s)
    #     print("Response 7:", response.message)
    
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    #     request = Message()
    #     request.set_op(CHECK_ACCOUNT)
    #     request.set_username("test_user_2")
    #     request.send_to_socket(s)
        
    #     response = Message()
    #     response.receive_from_socket(s)
    #     print("Response 8:", response.message)
    
    
    

