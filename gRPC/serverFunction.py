import service_pb2 as pb2
import service_pb2_grpc

import fnmatch
import threading


USERNAME_LIMIT = 20
MESSAGE_LIMIT = 500


SUCCESS = 0

 # error codes: range in [100, 199]
INVALID_USERNAME = 101
ACCOUNT_NOT_EXIST = 102
MESSAGE_TOO_LONG = 103
MESSAGE_ID_TOO_LARGE = 104
GENERAL_ERROR = 199


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


class ChatRoomServicer(service_pb2_grpc.ChatRoomServicer):
#  The followings are the server's functions.
#  Each function takes a request (a messsage object defined in protocol.py) as input,
#  and returns a response (also a message ojbect)

    def rpc_create_account(self, user, context):
        """ Create account with username [request.username].
            Respond error message if the account cannot be created.
        """
        username = user.username

        if len(username) > USERNAME_LIMIT:
            response = pb2.GeneralResponse(status=INVALID_USERNAME, message="Username too long.")
            return response
        
        print("create_account: waiting for lock....")
        shared_data.lock.acquire()
        print("create_account: acquired lock.")
        try:  
            if username in shared_data.accounts:
                response = pb2.GeneralResponse(status=GENERAL_ERROR, message=f"User [{username}] already exists!  Pick a different username.")
                print("    create_account: fail.")
            else:
                # Add the user to the account list.
                shared_data.accounts.append(username)
                # Initialize the user's message list to be empty.
                shared_data.messages[username] = []

                response = pb2.GeneralResponse(status=SUCCESS, message=f"Account [{username}] created successfully.  Please log in.")
                print("    create_account: success.")
        finally:
            shared_data.lock.release()
            print("create_account: released lock.")
        
        return response
