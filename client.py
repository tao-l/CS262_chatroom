import sys
import socket
import clientFunction
from clientFunction import *

HOST_PORT = 23333

def user_menu():
    """
    User Terminal Console
    It will keep prompting user for function number until a valid one
    """
    print('''
        {} CONNECTED TO MESSAGE SERVER - type the number of a function:
        (1) Create Account
        (2) Login to Account
        (3) List Accounts
        (4) Send a Message
        (5) Delete Account
        (6) Logout
        (7) Fetch Messages
        (8) Exit Program
    '''.format(clientFunction.myname))
    command = input('Input a number of the function >> ').strip()
    while command not in [str(i) for i in range(1,9)]:
        command = input('Input a number of the function >> ').strip()
    return int(command)

def handle_client_ui():
    """
    Catching illegal client actions before sending commands in to server
    """
    # get user input in command line
    menu_number = user_menu()
    # make sure user login or create account before doing anything else
    while clientFunction.myname == "" and menu_number not in [LIST_ACCOUNT_UI, LOGIN_ACCOUNT_UI, EXIT_PROGRAM_UI, CREATE_ACCOUNT_UI]:
        print("Please log in or create account first before doing other operations.")
        menu_number = user_menu()
    
    # no creating account when logged in
    while clientFunction.myname != "" and menu_number == CREATE_ACCOUNT_UI:
        print("Please log out to create a new account")
        menu_number = user_menu()

    # no double log in
    while clientFunction.myname != "" and menu_number == LOGIN_ACCOUNT_UI:
        print("Please log out to re login. ")
        menu_number = user_menu()

    # If client exits, no need to log off
    if menu_number == EXIT_PROGRAM_UI:
        sys.exit()

    return menu_number


if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("ERROR: Please use python client.py <host ip>. Port is fixed to 23333")
        sys.exit()
    
    # get ip address from command line 
    host_ip = str(sys.argv[1])
    
    login_just_success = False
    last_user_name = ''

    while True:
        
        # if the user newly login, automatically add a fetch message action
        if login_just_success and menu_number == LOGIN_ACCOUNT_UI:
            menu_number = FETCH_MESSAGE_UI
            login_just_success = False
            last_user_name = ''
        else: # just respond to client's acion
            menu_number = handle_client_ui() 
        
        # starting a client socket using TCP protocol
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(300)
            try:
                s.connect((host_ip, HOST_PORT))
            except:
                print("Error: Cannot connect to host {} port {}, try again.".format(host_ip, HOST_PORT))
                sys.exit()

            # Further prompt users to input details for each function,
            # Parse the input into command, and pass it to the socket
            # when sending fails, server or client crashes or are off line
            # for too long
            try:
                proceed_to_response = DISPATCH[menu_number](s)
            except:
                print("Send command operation failed, re-login and try again.")
                proceed_to_response = False
                s.close()
            
            # handle response from the server
            try:
                if proceed_to_response:
                #if menu_number not in (FETCH_MESSAGE_UI, LOGOUT_UI):
                    get_response(s, menu_number)
                    login_just_success =  last_user_name != clientFunction.myname
            except:
                print("Receive command operation failed, relog in and try again.")
            finally:
                s.close()
            

