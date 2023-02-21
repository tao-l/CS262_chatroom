# CS262_chatroom
## Demonstration
First, download or clone this github repository to the server and client machines.  To clone, cd into a folder where you want to put this repository and enter command: 
```console
$ git clone https://github.com/tao-l/CS262_chatroom.git
```
Then, cd into the repository: 
```console
$ cd CS262_chatroom
```
Now, you can __start the server__ by entering: 
```console
$ python3 server.py
```
The IP address of the server machine and the port it is listening at will be printed on the screen: 
```console
Network mode.
  Server's IP address: [IP_addr]
  Listening at port: 23333
```
If you only want to run the server and the client locally, you can start the server by entering: 
```console
$ python3 server.py local
```
In which case the server runs on the localhost 127.0.0.1. 

Then, on your client machine, __start the client__ with the server's IP address as a parameter (127.0.0.1 for the local mode):
```console
$ python3 client.py [IP_addr]
```
You can start multiple clients.  You can of course also start clients on the server's machine. 

Then, just play!

(To end the server or the client, press `control + c`.)

## gRPC
The above demonstration is for the socket implementation (which involves python programs `server.py`, `client.py`, `serverFunction.py`, `clientFunction.py`, `protocol.py`). To test the gRPC implementation, just cd into the gRPC folder 
```console
$ cd gRPC
```

First install gRPC to python using command
```console
$ python -m pip install grpcio
$ python -m pip install grpcio-tools
```

Then generate the grpc stub and skeleton code with commands
```console
$ python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. service.proto
```

and run the server and the client as before!
