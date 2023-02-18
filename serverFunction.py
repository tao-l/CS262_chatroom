from protocol import *
import fnmatch
import threading

MAX_USERS_TO_LIST = 100

# A data structure shared by all server threads, including: 
#    - a list of usernames of all existing accounts. 
#    - a dictionary mapping usernames to the set of messages they received. 
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
    
    print("Create_account waiting for lock")
    shared_data.lock.acquire()
    try:
        print("Create_account acquired lock.  Creating account...")
        
        if username in shared_data.accounts:
            response.set_status(GENERAL_ERROR)
            response.set_message(f"User [{username}] already exists!  Pick a different username.")
        else:
            shared_data.accounts.append(username)
            shared_data.messages[username] = []
            response.set_status(SUCCESS)
            response.set_message(f"Account [{username}] created successfully.  Please log in.")
    finally:
        shared_data.lock.release()
        print("Create_account released lock")
    
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
        All the messages received by this accounts are discarded (including undelivered ones). 
    """
    response = Message(request.op)
    username = request.username
    
    print("Delete_account waiting for lock")
    shared_data.lock.acquire()
    try:
        print("Delete_account acquired lock.")
        
        if username not in shared_data.accounts:
            response.set_status(ACCOUNT_NOT_EXIST)
            response.set_message(f"User [{username}] does not exist!")
        else:
            shared_data.accounts.remove(username)
            shared_data.messages.pop(username)
            response.set_status(SUCCESS)
            response.set_message(f"Account [{username}] deleted.  All received messages are deleted.")
    finally:
        shared_data.lock.release()
        print("Delete_account released lock")
    
    return response


def send_message(conn, user, shared):
    pass


def fetch_message(conn, user, shared):
    pass


DISPATCH = { CREATE_ACCOUNT: create_account,
             CHECK_ACCOUNT: check_account,
             LIST_ACCOUNT: list_account,
             DELETE_ACCOUNT: delete_account,
             SEND_MESSAGE: send_message,
             FETCH_MESSAGE: fetch_message
           }
