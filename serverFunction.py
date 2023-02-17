import protocol
import fnmatch
from protocol import *




def create_account(conn, request, current_user, shared_data):
    username = request.username
    if len(username) > USERNAME_LIMIT:
        response = protocol.Message(request.op, INVALID_USERNAME, "", "Invalid username.")
        return response
    
    print("Creat_account waiting for lock")
    shared_data["lock"].acquire()
    try:
        print("Creat_account got lock.  Creating account...")
        
        if username in shared_data["accounts"]:
            response = protocol.Message(request.op, GENERAL_ERROR, "", "User [{}] already exists!  Pick a different username.".format(username))
        else:
            shared_data["accounts"].append(username)
            response = protocol.Message(request.op, 0, "", "Account [{}] created successfully.  Please log in.".format(username))
    finally:
        shared_data["lock"].release()
        print("Creat_account releases lock")
    
    return response


def login_account(conn, user, shared):
    pass


def list_account(conn, request, current_user, shared_data):
    res = ""
    wildcard = request.message
    cnt = 0
    for username in shared_data["accounts"]:
        if fnmatch.fnmatch(username, wildcard):
            cnt += 1
            res += username + "\n"
            if cnt >= MAX_USERS_TO_LIST:
                res += "...\nToo many users. Only list {} users.\n".format(MAX_USERS_TO_LIST)
                break 
    response = protocol.Message(request.op, 0, "", res)
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
             LOGIN_ACCOUNT: login_account,
             LIST_ACCOUNT: list_account,
             SEND_MESSAGE: send_message,
             DELETE_ACCOUNT: delete_account,
             LOGOUT: logout,
             FETCH_MESSAGE: fetch_message
           }
