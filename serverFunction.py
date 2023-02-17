import fnmatch
from protocol import *

MAX_USERS_TO_LIST = 100

def create_account(request, shared_data):
    """ Create account with username [request.username].
        Respond error message if cannot create that account.
    """
    username = request.username
    if len(username) > USERNAME_LIMIT:
        response = Message(request.op, INVALID_USERNAME)
        response.set_message("Username too long.")
        return response
    
    print("Create_account waiting for lock")
    shared_data.lock.acquire()
    try:
        print("Create_account acquired lock.  Creating account...")
        
        if username in shared_data.accounts:
            response = Message(request.op, GENERAL_ERROR)
            response.set_message(f"User [{username}] already exists!  Pick a different username.")
        else:
            shared_data.accounts.append(username)
            response = Message(request.op, 0)
            response.set_message(f"Account [{username}] created successfully.  Please log in.")
    finally:
        shared_data.lock.release()
        print("Create_account released lock")
    
    return response


def check_account(request, shared_data):
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


def list_account(request, shared_data):
    result = ""
    wildcard = request.message
    cnt = 0
    for username in shared_data.accounts:
        if fnmatch.fnmatch(username, wildcard):
            cnt += 1
            result += username + "\n"
            if cnt >= MAX_USERS_TO_LIST:
                result += "...\nToo many users. Only list {} users.\n".format(MAX_USERS_TO_LIST)
                break 
    response = Message(request.op, SUCCESS)
    response.set_message(result)
    return response


def send_message(conn, user, shared):
    pass


def delete_account(conn, user, shared):
    pass


def logout(conn, user, shared):
    pass


def fetch_message(conn, user, shared):
    pass


DISPATCH = { CREATE_ACCOUNT: create_account,
             CHECK_ACCOUNT: check_account,
             LIST_ACCOUNT: list_account,
             SEND_MESSAGE: send_message,
             DELETE_ACCOUNT: delete_account,
             LOGOUT: logout,
             FETCH_MESSAGE: fetch_message
           }
