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


def create_account(socket):
    name = input("Input a username with alphabets and numeric of max length 12 >>").split()
    while not name.isalnum() or len(name)>12:
        name = input("Input a username with alphabets and numeric of max length 12 >>").split()

    msg_obj = ClientMessage(CREATE_ACCOUNT,name)
    msg_obj.send_to_socket(socket)

    

DISPATCH = { CREATE_ACCOUNT: create_account,
             LOGIN_ACCOUNT: login_account,
             LIST_ACCOUNT: list_account,
             SEND_MESSAGE: send_message,
             DELETE_ACCOUNT: delete_account,
             LOGOUT: logout,
             FETCH_MESSAGE: fetch_message,
             EXIST_PROGRAM: exist_program}

