"""
CS 262 Distributed System
Created on Feb 16, 2023
Author: Gary Ma, Tao Lin
"""
from protocol import *


####################################
###### Handle Message Sent    ######
####################################

def client_send_message(msg_obj, socket):
    """
    Wrapper for client send message.
    Return:
        success or failure
    Throw error if:
        1) server socket.close/crash, error: connection terminated by the other side
        2) Send all did not send all data: which error?
        3) Time out: server taking too long to reply. timeout error
    In all three cases, the connection is down and the upstream code should reinitialize client socket.
    """
    try:
        msg_obj.send_to_socket()
        return True
    except:
        print("Error: failed to send message.") # log in and try again
        raise RuntimeError

def create_account(socket):
    """
    User creating an account of alphabets and numeric of max length 12
    Return:
        true if account name is sent over to server
        false if failed to send all messages to server
    """
    name = input("Input a username with alphabets and numeric of max length 12 >>").strip()
    while not name.isalnum() or len(name)>12:
        name = input("Input a username with alphabets and numeric of max length 12 >>").strip()

    msg_obj = ClientMessage(op=CREATE_ACCOUNT, username=name)
    # throw exception in the next line if send error encountered
    success = client_send_message(msg_obj, socket)
    return success

def login_account(socket):
    """
    User log in some account after creating an account 
    """
    name = input("Input a user name to log in").strip()
    while not name.isalnum() or len(name)>12:
        name = input("Input a user name to log in").strip()
    msg_obj = ClientMessage(op=LOGIN_ACCOUNT, username=name)
    # throw exception in the next line if send error encountered
    success = client_send_message(msg_obj, socket)
    return sucess

def list_account(socket):
    """
    List account name with wildcard
    """
    msg = input("Input a username search patter with alphabets, numeric and wildcard *").strip()
    msg_obj = ClientMessage(op=LIST_ACCOUNT, message=msg)
    success = client_send_message(msg_obj, socket)
    return success

def send_message(socket):
    """
    User send message to another user
    """
    msg = input("To which other use")

DISPATCH = { CREATE_ACCOUNT: create_account,
             LOGIN_ACCOUNT: login_account,
             LIST_ACCOUNT: list_account,
             SEND_MESSAGE: send_message,
             DELETE_ACCOUNT: delete_account,
             LOGOUT: logout,
             FETCH_MESSAGE: fetch_message,
             EXIST_PROGRAM: exist_program}

####################################
###### Handle Message Receipt ######
####################################

def client_receive_message(socket):
    """
    Wrapper for client receive message.
    Return:
        a message object
    Throw error if:
        1) server crashes -- throw an error, connection terminated by the other side
        2) server network out -- keeps listening until time out, time out error
        3) receive zero byte -- receive_n_byte throws a runtime error
    In all three cases, the connection is down and the upstream code should reinitialize client socket.
    """
    request = protocol.Message()
    try:
        request.receive_from_socket(socket)
        print("Received from server:", request.op, request.status, request.username)
        return request
    except Exception as err:
        print("Error: failed to receive server message.") # log in and try again
        raise RuntimeError    



# After sending a command to a server, receives a reply from the server
def get_response(socket, menu_number):

    # If message receive failed, throws an error next line 
    msg_obj = client_receive_message(socket)
    
    # operation code has to be valid, else raise an error
    if msg_obj.op not in DISPATH:
        print("Error: server returning operation {}, invalid!".format(msg_obj.op))
        raise RuntimeError
     
    # parsing info
    # For every operation, regardless of success or failure, message already encoded
    print(msg_obj.message)
