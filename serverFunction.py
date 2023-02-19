from protocol import *
import fnmatch
import threading

MAX_USERS_TO_LIST = 100

# A data structure shared by all server threads, including: 
#    - a list of all existing accounts/users (identified by their usernames) 
#    - a dictionary mapping users to the set of messages they received.
#      Specifically, messages[user_a] is a list of (user, message) pairs
#      recoding the messages user_a received (and from which user):  
#          messages[user_a] = [ (user_1, message_1), (user_2, message_2), ..., ] 
#    - a lock for the shared data structure. 
class SharedData():
    def __init__(self):
        self.accounts = []
        self.messages = {}
        self.lock = threading.Lock()

shared_data = SharedData()


#  The followings are the server's functions.
#  Each function takes a request (a messsage object defined in protocol.py) as input,
#  and returns a response (also a message ojbect)

def create_account(request):
    """ Create account with username [request.username].
        Respond error message if the account cannot be created.
    """
    response = Message(request.op)
    username = request.username

    if len(username) > USERNAME_LIMIT:
        response.set_status(INVALID_USERNAME)
        response.set_message("Username too long.")
        return [ response ]
    
    print("create_account: waiting for lock....")
    shared_data.lock.acquire()
    print("create_account: acquired lock.")
    try:  
        if username in shared_data.accounts:
            response.set_status(GENERAL_ERROR)
            response.set_message(f"User [{username}] already exists!  Pick a different username.")
            print("    create_account: fail.")
        else:
            # Add the user to the account list.
            shared_data.accounts.append(username)
            # Initialize the user's message list to be empty.
            shared_data.messages[username] = []

            response.set_status(SUCCESS)
            response.set_message(f"Account [{username}] created successfully.  Please log in.")
            print("    create_account: success.")
    finally:
        shared_data.lock.release()
        print("create_account: released lock.")
    
    return [ response ]


def check_account(request):
    """ Checks whether the account [request.username] exists in the account list. 
        Respond: yes or no. 
    """
    response = Message(request.op)
    if request.username in shared_data.accounts:
        response.set_status(SUCCESS)
        response.set_message("Account exists.")
    else:
        response.set_status(ACCOUNT_NOT_EXIST)
        response.set_message("Account does not exist.")
    return [ response ]


def list_account(request):
    """ - List accounts that match with the wildcard in [request.message].
        - Return a list of those accounts in a single message object.
          Because the message object has a length limit, only return MAX_USERS_TO_LIST accounts
          if there are too many such accounts.
    """
    response_list = []
    wildcard = request.message
    for username in shared_data.accounts:
        if fnmatch.fnmatch(username, wildcard):
            response = Message(request.op, NEXT_ELEMENT_EXIST, username)
            response_list.append(response)

    if response_list == []:
        response_list = [ Message(request.op, NO_ELEMENT, "", "", "No matched account.") ]
    else:
        # change the status code of the last resopnse to be NO_NEXT_ELEMENT
        response_list[-1].set_status(NO_NEXT_ELEMENT)
    
    return response_list


def delete_account(request):
    """ Delete the account with [request.username].
        Return error message if the account does not exists.
        All the messages received by this account are discarded (including undelivered ones). 
    """
    response = Message(request.op)
    username = request.username
    
    print("delete_account: waiting for lock...")
    shared_data.lock.acquire()
    print("delete_account: acquired lock.")    
    try:
        if username not in shared_data.accounts:
            response.set_status(ACCOUNT_NOT_EXIST)
            response.set_message(f"User [{username}] does not exist!")
        else:
            # Remove the user from the account list
            shared_data.accounts.remove(username)
            # Remove the user's message list.
            shared_data.messages.pop(username)
            response.set_status(SUCCESS)
            response.set_message(f"Account [{username}] deleted.  All received messages are discarded.")
    finally:
        shared_data.lock.release()
        print("delete_account: released lock.")
    
    return [ response ]


def send_message(request):
    """ Send a message from [request.username] to [request.target_name]: 
        - If [request.username] or [request.target_name] does not exist, return error
        - If message is too long, return error
        - Otherwise, update shared_data.messages, return SUCCESS
    """
    response = Message(request.op)
    username = request.username
    target_name = request.target_name
    msg = request.message

    if len(msg) > MESSAGE_LIMIT:
        request.set_status(MESSAGE_TOO_LONG)
        response.set_message(f"Message longer than {MESSAGE_LIMIT}, cannot be sent!")
        return [ response ]

    print("send_messgage: waiting for lock...")
    shared_data.lock.acquire()
    print("send_message: acquired lock. ")
    try:
        if username not in shared_data.accounts:
            response.set_status(ACCOUNT_NOT_EXIST)
            response.set_message(f"Your account [{username}] does not exist!")
        elif target_name not in shared_data.accounts:
            response.set_status(ACCOUNT_NOT_EXIST)
            response.set_message(f"Target user [{target_name}] does not exist!")
        else:
            # add the pair (username, message) to the target user's message list
            shared_data.messages[target_name].append( (username, request.message) )
            response.set_status(SUCCESS)
            response.set_message("Message sent succesfully.")
    finally:
        shared_data.lock.release()
        print("send_message: released lock. ")
    
    return [ response ]


def fetch_message(request):
    """ Client fetches message sent to the user [request.username].
        Client specifies a [msg_id] in [request.status]: 
        Server tries to return all the messages sent to the user starting from the (msg_id)-th one:   
        - If the client's username does not exist, return error. 
        - If [msg_id] < 1, return error. 
        - If [msg_id] is larger than the number of messages the client received, return NO_ELEMENT
        - Otherwise, return a stream of responses, where each response includes 
            * the message in [response.message]
            * the user who sent this message in [response.username]
            * and specify whether there are more responses in [response.status]:
              - if there are, [response.status] = NEXT_ELEMENT_EXIST
              - if not, [response.status] = NO_NEXT_ELEMENT
    """
    username = request.username
    msg_id = request.status

    if msg_id < 1:
        response = Message(request.op, GENERAL_ERROR)
        response.set_message("Message id < 1")
        return [ response ]
    
    print("fetch_messgage: waiting for lock...")
    shared_data.lock.acquire()
    print("fetch_message: acquired lock. ")
    try:
        if username not in shared_data.accounts:
            response = Message(request.op, ACCOUNT_NOT_EXIST)
            response.set_message(f"Your account [{username}] does not exist!")
            response_list = [response]
            return    # this return will go to the "finally" block, not ending the function. 
        
        total_msg = len(shared_data.messages[username])
        if msg_id > total_msg:
            response = Message(request.op, NO_ELEMENT)
            response.set_message(f"Message id {msg_id} > total number of messages {total_msg}")
            response_list = [response]
            return    # this return will go to the "finally" block, not ending the function. 
        
        response_list = []
        for i in range(msg_id-1, total_msg):
            (from_which_user, message) = shared_data.messages[username][i]
            response = Message(request.op)
            response.set_username( from_which_user )
            response.set_message( message )
            if i == total_msg - 1:
                response.set_status(NO_NEXT_ELEMENT)
            else:
                response.set_status(NEXT_ELEMENT_EXIST)
            response_list.append(response)
                    
    finally:
        shared_data.lock.release()
        print("fetch_message: released lock. ")
        return response_list


DISPATCH = { CREATE_ACCOUNT: create_account,
             CHECK_ACCOUNT: check_account,
             LIST_ACCOUNT: list_account,
             DELETE_ACCOUNT: delete_account,
             SEND_MESSAGE: send_message,
             FETCH_MESSAGE: fetch_message
           }
