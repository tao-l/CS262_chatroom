"""
CS 262 Distributed System
Created on Feb 16, 2023
Author: 
"""
from serverFunction import *
import service_pb2 as pb2
import service_pb2_grpc

myname = "" # global variable for the client program to know who I am
mymsgcount = 1 # global variable for the client 

CREATE_ACCOUNT_UI = 1
LOGIN_ACCOUNT_UI = 2
LIST_ACCOUNT_UI = 3
SEND_MESSAGE_UI = 4
DELETE_ACCOUNT_UI = 5
LOGOUT_UI = 6
FETCH_MESSAGE_UI = 7
EXIT_PROGRAM_UI = 8


def create_account(stub):
    """
    User creating an account of alphabets and numeric of max length 12
    """
    name = input("Input a username with alphabets and numeric of max length {} >> ".format(USERNAME_LIMIT)).strip()
    while not name.isalnum() or len(name) > USERNAME_LIMIT:
        print("Username contains illegal character or is too long.")
        name = input("Input a username with alphabets and numeric of max length {} >> ".format(USERNAME_LIMIT)).strip()
    
    user = pb2.User()
    user.username = name
    response = stub.rpc_create_account(user)
    #print("length of response create account", response.ByteSize())
    print(response.message)
    return

def login_account(stub):
    """
    User log in an account after creating an account
    It sends a request to server to verify if this account exists
    The server won't store the log in information
    This log in is only for the local program to store the global variable myname
    """
    name = input("Input a user name to log in >> ").strip()
    while not name.isalnum() or len(name)> USERNAME_LIMIT:
        print("Username contains illegal character or is too long.")
        name = input("Input a user name to log in >> ").strip()
    

    user = pb2.User()
    user.username = name
    response = stub.rpc_check_account(user)
    if response.status == SUCCESS:
        global myname
        myname = name
        print("Login success for account {}.".format(myname))
        fetch_message(stub)
    elif response.status == ACCOUNT_NOT_EXIST:
        print("Account does not exist.")


def list_account(stub):
    """
    List account name with wildcard, only * is supported
    return:
        proceed to response true
    """
    msg = input("Input a username search pattern with alphabets, numeric and wildcard * >> ").strip()
    while (not msg.replace("*","").isalnum() and msg != "*"):
        print("Username pattern is illegal.")
        msg = input("Input a username search patter with alphabets, numeric and wildcard * >> ").strip()

    wildcard = pb2.Wildcard()
    wildcard.wildcard = msg
    response_len = 0
    for user in stub.rpc_list_account(wildcard):
        response_len += 1
        print(user.username)

    if not response_len:
        print("No accounts conforming with pattern "+msg)
    else:
        print("All accounts names conforming with patterns listed.")


def send_message(stub):
    """
    User send message to another user.
    return:
        proceed to response true
    """
    target_name = input("Specify a target name with alphabets and numeric of max length {} >> ".format(USERNAME_LIMIT)).strip()
    while not target_name.isalnum() or len(target_name)> USERNAME_LIMIT:
        target_name = input("Specify a target name with alphabets and numeric of max length {} >> ".format(USERNAME_LIMIT)).strip()
    
    msg = input("Input your message of max length {} characters >> ".format(MESSAGE_LIMIT))
    while len(msg) > MESSAGE_LIMIT:
        print("Message length longer than {}".format(MESSAGE_LIMIT))
        msg = input("Input your message of max length {} characters >> ".format(MESSAGE_LIMIT))

    chat_msg = pb2.ChatMessage() 
    chat_msg.username = myname
    chat_msg.target_name = target_name
    chat_msg.message = msg
    response = stub.rpc_send_message(chat_msg)
    print(response.message)
    

def delete_account(stub):
    """
    A logged in user delete its account
    This automatically logs out a user
    return:
        proceed to response. If no need to delete account, return false
    """
    msg = input("Are you sure to delete account {}(Y/N) >> ".format(myname))
    while msg not in ["Y","N"]:
        msg = input("Are you sure to delete account {}(Y/N) >> ".format(myname))

    if msg == "N": return

    user = pb2.User()
    user.username = myname
    response = stub.rpc_delete_account(user)
    print(response.message)
    if response.status == SUCCESS:
        print("Automatically logging out of account {}".format(myname))
        logout(stub)


def logout(stub):
    """
    The server does not need to know a client is logged off.
    Logging off here is only updating the global variable myname to ""
    Return:
        proceed to response: no need to listen to server's response
    """
    global myname
    global mymsgcount
    myname = ""
    mymsgcount = 1
    print("Log out successful.")
    return False


def fetch_message(stub):
    """
    The client keeps a counter mymsgcount for fetching through all historical msg.
    When client/server crash, the counter mymsgcount restarts from 0 again. 
    fetch message handles message receives itself.
    return:
        proceed to response: no need to listen to server's response
    """
    global mymsgcount
    fetch_request = pb2.FetchRequest()
    fetch_request.msg_id = mymsgcount
    fetch_request.username = myname
    for chat_msgs in stub.rpc_fetch_message(fetch_request):
        if chat_msgs.status in (NO_NEXT_ELEMENT, NEXT_ELEMENT_EXIST):
            print(chat_msgs.username+" : " + chat_msgs.message)
            mymsgcount += 1
        elif chat_msgs.status == ACCOUNT_NOT_EXIST:
            print(chat_msgs.message)
        elif chat_msgs.status == NO_ELEMENT:
            print("No new messages.")
        
    
DISPATCH = { CREATE_ACCOUNT_UI: create_account,
             LOGIN_ACCOUNT_UI: login_account,
             LIST_ACCOUNT_UI: list_account,
             SEND_MESSAGE_UI: send_message,
             DELETE_ACCOUNT_UI: delete_account,
             LOGOUT_UI: logout,
             FETCH_MESSAGE_UI: fetch_message}


