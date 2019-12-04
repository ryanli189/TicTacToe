from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys
import time

placePiece = False
invalidMove = True
endOption = False

welcomeMsg = 'Welcome to TicTacToe! Please type your name and press enter.'
inQueueMsg = 'Please wait. Looking for another player.'
invalidMoveError = 'Error: invalid move. Choose a valid location.'
yourTurnMsg = "You're up. Choose a valid locaiton to place a piece."
endOptionMsg = 'Enter "Q" to quit. Enter "R" (or any other character) for rematch.'

# Set up client, connect to host
HOST = input('Enter server name:\n... ')
serverPort = 2019
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((HOST,serverPort))

#Make move
def play():
    global invalidMove
    while True:
        loc = input('... ')
        clientSocket.send(loc.encode())
        time.sleep(0.5)
        if not invalidMove:
            invalidMove = True
            break

def receive():
    global placePiece
    global invalidMove
    global yourTurnMsg
    global invalidMoveError
    global endOption
    while True:
        try:
            msg = clientSocket.recv(1024).decode()
            print(msg)
            if yourTurnMsg in msg:
                placePiece = True
            elif endOptionMsg in msg:
                endOption = True
            elif "Error: invalid move." not in msg:
                invalidMove = False
            elif "Ending game." in msg:
                sys.exit()
        except OSError:
            print("End")
            # Possibly client has left the chat.
            break

def send():  
    global placePiece
    global endOption
    while True:
        try:
            if endOption:
                choice = input('... ')
                clientSocket.send(choice.encode())
                endOption = False
            if placePiece:
                play()
                placePiece = False
        except OSError:
            # Possibly client has left the chat.
            break

def main():
    # Handshake steps:
    # 1. Client receives greeting message from chat server, asking for a name
    print(clientSocket.recv(1024).decode())
    # 2. Client enters name and sends it to chat server
    NAME = input('... ')
    clientSocket.send(NAME.encode())

    # Start the receiving thread
    receive_thread = Thread(target=receive)
    receive_thread.start()
    # Start the sending thread
    send_thread = Thread(target=send)
    send_thread.start()

    # Wait for child threads to stop
    receive_thread.join()
    send_thread.join()

if __name__ == "__main__":
    main()