"""
CS 262 Distributed System
Created on Feb 16, 2023
Author: Gary Ma, Tao Lin
"""
from potocol import *

CREATE_ACCOUNT = 1
LOGIN_ACCOUNT = 2
LIST_ACCOUNT = 3
SEND_MESSAGE = 4
DELETE_ACCOUNT = 5
LOGOUT = 6
FETCH_MESSAGE = 7
EXIST_PROGRAM = 8

def client_send_message(msg_obj, socket):
    """
    Wrapper for client send message. Three kinds of error can occur
    1) Seller socket.close, seller shut down throws error
    2) Send all did not send all data
    3) Time out
    """
    try:
        error = msg_obj.send_to_socket()
    except:
        error = True
        print("Error: failed to send message.") # log in and try again
        raise RuntimeError
    return not error

def create_account(socket):
    """
    User creating an account of alphabets and numeric of max length 12
    Return:
        true if account name is sent over to server
        false if failed to send all messages to server
    """
    name = input("Input a username with alphabets and numeric of max length 12 >>").split()
    while not name.isalnum() or len(name)>12:
        name = input("Input a username with alphabets and numeric of max length 12 >>").split()

    msg_obj = ClientMessage(CREATE_ACCOUNT,name)
    success = client_send_message(msg_obj, socket)
    return success

def login_account(socket):
    """

    """

def get_response(socket, menu_number):
    

DISPATCH = { CREATE_ACCOUNT: create_account,
             LOGIN_ACCOUNT: login_account,
             LIST_ACCOUNT: list_account,
             SEND_MESSAGE: send_message,
             DELETE_ACCOUNT: delete_account,
             LOGOUT: logout,
             FETCH_MESSAGE: fetch_message,
             EXIST_PROGRAM: exist_program}

