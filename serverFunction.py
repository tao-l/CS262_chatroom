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
        return response
    
    print("create_account: waiting for lock....")
    shared_data.lock.acquire()
    print("create_account: acquired lock.")
    try:  
        if username in shared_data.accounts:
            response.set_status(GENERAL_ERROR)
            response.set_message(f"User [{username}] already exists!  Pick a different username.")
        else:
            # add the user to the account list
            shared_data.accounts.append(username)
            # Initialize the user's message list to be empty.
            shared_data.messages[username] = []

            response.set_status(SUCCESS)
            response.set_message(f"Account [{username}] created successfully.  Please log in.")
    finally:
        shared_data.lock.release()
        print("create_account: released lock.")
    
    return response


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
    return response


def list_account(request):
    """ - List accounts that match with the wildcard in [request.message].
        - Return a list of those accounts in a single message object.
          Because the message object has a length limit, only return MAX_USERS_TO_LIST accounts
          if there are too many such accounts.
    """
    result = ""
    wildcard = request.message
    cnt = 0
    for username in shared_data.accounts:
        if fnmatch.fnmatch(username, wildcard):
            cnt += 1
            result += username + "\n"
            if cnt >= MAX_USERS_TO_LIST:
                result += f"...\nToo many users. Only list {MAX_USERS_TO_LIST} users.\n"
                break 
    response = Message(request.op, SUCCESS)
    response.set_message(result)
    return response


def delete_account(request):
    """ Delete the account with [request.username]
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
        print("delete_account: released lock")
    
    return response


def send_message(request):
    """ Send a message from [request.username] to [request.target_name]
        - If [request.username] or [request.target_name] does not exist, return error
        - If message is too long, return error
        - Otherwise, update shared_data.messages, return SUCESS
    """
    response = Message(request.op)
    username = request.username
    target_name = request.target_name
    msg = request.message

    if len(msg) > MESSAGE_LIMIT:
        request.set_status(MESSAGE_TOO_LONG)
        response.set_message(f"Message longer than {MESSAGE_LIMIT}, cannot be sent!")
        return response

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
    
    return response


def fetch_message(request):
    """ Client fetches a single message received by the user [request.username]. 
        Which message to fecth is specified in [request.status]: 
            msg_id = request.status
        Server tries to return the (msg_id)-th message to the client:  
        - If the client's username does not exist, return Error. 
        - If msg_id < 1 or is more than the number of messages the client received,
            return Error
        - Otherwise, return
            * the message in [response.message]
            * the user who sent this message in [response.username]
            * and specify whether there are more messages to be fetched in [response.status]:
              - if there are, [response.status] = NEXT_MESSAGE_EXIST
              - if not, [response.status] = NO_NEXT_MESSAGE
    """
    response = Message(request.op)
    username = request.username
    msg_id = request.status

    if (msg_id < 1):
        response.set_status(GENERAL_ERROR)
        response.set_message("Message id < 1")
        return response
    
    print("fetch_messgage: waiting for lock...")
    shared_data.lock.acquire()
    print("fetch_message: acquired lock. ")
    try:
        if username not in shared_data.accounts:
            response.set_status(ACCOUNT_NOT_EXIST)
            response.set_message(f"Your account [{username}] does not exist!")
        else:
            total_msg = len(shared_data.messages[username])
            if msg_id > total_msg:
                response.set_status(MESSAGE_ID_TOO_LARGE)
                response.set_message(f"Message id {msg_id} > total number of messages {total_msg}")
            else:
                (from_which_user, message) = shared_data.messages[username][msg_id - 1]
                response.set_username( from_which_user )
                response.set_message( message )
                if msg_id < total_msg:
                    response.set_status(NEXT_MESSAGE_EXIST)
                else:
                    response.set_status(NO_NEXT_MESSAGE)
    finally:
        shared_data.lock.release()
        print("fetch_message: released lock. ")
    
    return response


DISPATCH = { CREATE_ACCOUNT: create_account,
             CHECK_ACCOUNT: check_account,
             LIST_ACCOUNT: list_account,
             DELETE_ACCOUNT: delete_account,
             SEND_MESSAGE: send_message,
             FETCH_MESSAGE: fetch_message
           }
