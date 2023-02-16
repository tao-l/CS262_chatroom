"""
CS 262 Distributed System
Created on Feb 16, 2023
Author: Gary Ma, Tao Lin
"""

import sys
import socket
from clientFunction import *


def user_menu():
    """
    User Terminal Console
    It will keep prompting user for function number until a valid one
    """
    print('''
        CONNECTED TO MESSAGE SERVER - type the number of a function:
        (1) Create Account
        (2) Login to Account
        (3) List Accounts
        (4) Send a Message
        (5) Delete Account
        (6) Logout
        (7) Fetch Messages
        (8) Exit Program
    ''')
    command = int(input('Input a number of the function >> ').strip())
    while command not in list(range(1,9)):
        command = int(input('Input a number of the function >> ').strip())
    return command


if __name__ == "__main__":
    if len(sys.argv))!=3:
        print("ERROR: Please use python client.py <host ip> <port>.")
        sys.exit()

    # get ip address and ports from command line 
    host_ip = sys.argv[1]
    host_port = sys.argv[2]
    
    # starting a client socket using TCP protocol
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host_ip, host_port))
        except:
            print("Error: Cannot connect to host {} port {}".format(host_ip, host_port))
            sys.exit()

        while True:
            menu_number = user_menu()

            # Further prompt users to input details for each function,
            # Parse the input into command, and pass it to the socket
            DISPATCH[menu_number](s)

            getResponse(s, menu_number)
            
            if menu_number == EXIT_PROGRAM:
                break
