from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys

placePiece = False

#Make move
def play(clientSocket):
    x = input('Enter column number (0, 1, or 2) 0 being the left most column\n... ')
    clientSocket.send(x.encode())
    y = input('Enter row number (0, 1, or 2) 0 being the top most row\n... ')
    clientSocket.send(y.encode())

# print(clientSocket.recv(1024).decode()) #Receive initial welcome message
# name = input('... ') #Input username
# clientSocket.send(name.encode())

# message = clientSocket.recv(1024).decode()
# print(message)
# if 'Please wait' in message: #If first player to join wait for second and then recieve matchup information
#     print(clientSocket.recv(1024).decode())

# while True: #Matchup simulation
#     gameRoundInfo = clientSocket.recv(1024).decode()
#     print(gameRoundInfo) #Print game round information

#     #If going second
#     if (name + ' is second') in gameRoundInfo:
#         print("Going second")
#         print(clientSocket.recv(1024).decode()) #Print other player's move

#     while True: #Game simulation
#         #Play
#         message = play(clientSocket)
#         while 'Error' in message: # If recevied error message keep playing until not error message
#             message = play(clientSocket)
        
#         #Watch
#         message = clientSocket.recv(1024).decode()
#         print(message)
#         if 'Game Over' in message:
#             print(clientSocket.recv(1024).decode())
#             break

# clientSocket.close

def receive(clientSocket):
    while True:
        try:
            msg = clientSocket.recv(1024).decode()
            if "You're up." in msg:
                placePiece = True
            print(msg)
        except OSError:
            # Possibly client has left the chat.
            break

def send(clientSocket):  
    while True:
        try:
            if placePiece:
                play(clientSocket)
                placePiece = False
        except OSError:
            # Possibly client has left the chat.
            break

def main():
    # Set up client, connect to host
    HOST = input('Enter server name: ')
    serverPort = 2019
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((HOST,serverPort))
    # Handshake steps:
    # 1. Client receives greeting message from chat server, asking for a name
    print(clientSocket.recv(1024).decode())
    # 2. Client enters name and sends it to chat server
    NAME = input('... ')
    clientSocket.send(NAME.encode())

    # Start the receiving thread
    receive_thread = Thread(target=receive, args=(clientSocket))
    receive_thread.start()

    # Start the sending thread
    send_thread = Thread(target=send, args=(clientSocket))
    send_thread.start()

    # Wait for child threads to stop
    receive_thread.join()
    send_thread.join()

if __name__ == "__main__":
    main()