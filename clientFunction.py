from protocol import *
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
    request = Message()
    try:
        request.receive_from_socket(socket)
        #print("Received from server:", request.op, request.status, request.username)
        return request
    except Exception as err:
        print("Error: failed to receive server message.") # log in and try again
        raise RuntimeError


# After sending a command to a server, receives a reply from the server
def get_response(socket, menu_number):

    # If message receive failed, throws an error next line 
    msg_obj = client_receive_message(socket)
     
    # parsing info
    # For every operation, regardless of success or failure, message already encoded
    
    if menu_number not in {FETCH_MESSAGE_UI, LIST_ACCOUNT_UI}:
        if msg_obj.status == SUCCESS:
            print_green(msg_obj.message)
        else:
            print_red("Error: " + msg_obj.message)

    ###########################################################
    # handle post response operations, customize return message
    ###########################################################

    if menu_number == LOGIN_ACCOUNT_UI:
        # login failure ---- account does not exist yet
        # set back the myname to empty
        if msg_obj.status != SUCCESS:
            global myname
            myname = ""
        # login success ---- fetch all previous messages
        # have to reinitialize a socket outside because the server no longer listens
        elif msg_obj.status == SUCCESS:
            print("Login success for account {}.".format(myname))

    # logging out account when successfully deleting
    elif menu_number == DELETE_ACCOUNT_UI:
        if msg_obj.status == SUCCESS:
            print("Account {} deleted. Automatically logging out.".format(myname))
            logout(socket)

    # list account recursively receives all account msgs server sends
    elif menu_number == LIST_ACCOUNT_UI:
        if msg_obj.status == NO_ELEMENT:
            print_red("No accounts found.")
        elif msg_obj.status == NEXT_ELEMENT_EXIST:
            print_yellow(msg_obj.username)
            get_response(socket, menu_number)
        elif msg_obj.status == NO_NEXT_ELEMENT:
            print_cyan(msg_obj.username)
            print("All accounts conforming with the pattern listed.")
        else:
            print_red("Error: " + msg_obj.message)

    # fetch message recursively receives all account msgs server sends
    elif menu_number == FETCH_MESSAGE_UI:
        if msg_obj.status not in (NO_ELEMENT, NEXT_ELEMENT_EXIST, NO_NEXT_ELEMENT):
            print_red("Error: " + msg_obj.message)
            return 
        if msg_obj.status == NO_ELEMENT:
            print("All messages fetched!")
            return
        print_yellow("{} : {}".format(msg_obj.username, msg_obj.message))
        global mymsgcount
        mymsgcount += 1 
        if msg_obj.status == NEXT_ELEMENT_EXIST:            
            get_response(socket, menu_number)



####################################
###### Handle Message Sent    ######
####################################

def client_send_message(msg_obj, socket):
    """
    Wrapper for client socket sending message to the server socket.
    Return:
        success or failure
    Throw error if:
        1) server socket.close/crash, error: connection terminated by the other side
        2) Send all did not send all data: which error?
        3) Time out: server taking too long to reply. timeout error
    In all three cases, the connection is down and the upstream code should reinitialize client socket.
    """
    try:
        msg_obj.send_to_socket(socket)
        return True
    except:
        print("Error: failed to send message.") # log in and try again
        raise RuntimeError

def create_account(socket):
    """
    User creating an account
    Return:
        proceed to response = true
    """
    name = input("Input a username with alphabets and numeric of max length {} >> ".format(USERNAME_LIMIT)).strip()
    while not name.isalnum() or len(name) > USERNAME_LIMIT:
        print("Username contains illegal character or is too long.")
        name = input("Input a username with alphabets and numeric of max length {} >> ".format(USERNAME_LIMIT)).strip()

    msg_obj = Message(op=CREATE_ACCOUNT, username=name)
    # throw exception in the next line if send error encountered
    client_send_message(msg_obj, socket)
    return True

def login_account(socket):
    """
    User log in an account after creating an account
    It sends a request to server to verify if this account exists
    The server won't store the log in information
    This log in is only for the local program to store the global variable myname
    Return:
        proceed to response = true
    """
    name = input("Input a user name to log in >> ").strip()
    while not name.isalnum() or len(name)> USERNAME_LIMIT:
        print("Username contains illegal character or is too long.")
        name = input("Input a user name to log in >> ").strip()

    # ask the server if the supplied user name is in the list
    msg_obj = Message(op=CHECK_ACCOUNT, username=name)
    # throw exception in the next line if send error encountered
    client_send_message(msg_obj, socket)
    # regardless of server confirming the name, store this name for now
    global myname
    myname = name
    return True


def list_account(socket):
    """
    List account name with wildcard, only * is supported
    return:
        proceed to response true
    """
    msg = input("Input a username search pattern with alphabets, numeric and wildcard * >> ").strip()
    while (not msg.replace("*","").isalnum() and msg != "*"):
        print("Username pattern is illegal.")
        msg = input("Input a username search patter with alphabets, numeric and wildcard * >> ").strip()

    msg_obj = Message(op=LIST_ACCOUNT, message=msg)
    # throw exception in the next line if send error encountered
    client_send_message(msg_obj, socket)
    return True


def send_message(socket):
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
    global myname
    msg_obj = Message(op=SEND_MESSAGE, username=myname, target_name=target_name, message=msg) 
    # throw exception in the next line if send error encountered
    client_send_message(msg_obj, socket)
    return True

def delete_account(socket):
    """
    A logged in user delete its account
    This automatically logs out a user
    return:
        proceed to response. If no need to delete account, return false
    """
    msg = input("Are you sure to delete account {} (Y/N) >> ".format(myname))
    while msg not in ["Y","N"]:
        msg = input("Are you sure to delete account {} (Y/N) >> ".format(myname))

    if msg == "N": return False
    msg_obj = Message(op=DELETE_ACCOUNT, username=myname)
    # throw exception in the next line if send error encountered
    success = client_send_message(msg_obj, socket)
    return True

def logout(socket):
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


def fetch_message(socket):
    """
    The client keeps a counter mymsgcount for fetching through all historical msg.
    When client/server crash, the counter mymsgcount restarts from 0 again. 
    fetch message handles message receives itself.
    return:
        proceed to response: true
    """
    global mymsgcount
    msg_obj = Message(FETCH_MESSAGE, mymsgcount, myname)
    # throw exception in the next line if send error encountered
    client_send_message(msg_obj, socket)
    
    return True
    """ 
    while True: # keep fetching messages until the last one
        request = Message(FETCH_MESSAGE, mymsgcount, myname)
        # throw exception in the next line if send error encountered
        success = client_send_message(msg_obj, socket)
        # receive from server how many more messages, throw exception in the next line if receive error encountered
        response = client_receive_message(socket)
        mymsgcount += 1
        print("  ", response.username, ":", response.message)
        
        if response.status == NO_NEXT_MESSAGE:
            print("Finished fetching all messages.")
            break
        # else status is NEXT_MESSAGE_EXIST
    return False
    """


DISPATCH = { CREATE_ACCOUNT_UI: create_account,
             LOGIN_ACCOUNT_UI: login_account,
             LIST_ACCOUNT_UI: list_account,
             SEND_MESSAGE_UI: send_message,
             DELETE_ACCOUNT_UI: delete_account,
             LOGOUT_UI: logout,
             FETCH_MESSAGE_UI: fetch_message}



def print_red(text):
    print('\033[0;31;40m' + text + '\033[0m')

def print_green(text):
    print('\033[0;32;40m' + text + '\033[0m')

def print_cyan(text):
    print('\033[0;34;40m' + text + '\033[0m')

def print_yellow(text):
    print('\033[0;33;40m' + text + '\033[0m')
