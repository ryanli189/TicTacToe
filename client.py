from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys

placePiece = False

# Set up client, connect to host
HOST = input('Enter server name: ')
serverPort = 2019
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((HOST,serverPort))

#Make move
def play():
    x = input('Enter column number (0, 1, or 2) 0 being the left most column\n... ')
    clientSocket.send(x.encode())
    y = input('Enter row number (0, 1, or 2) 0 being the top most row\n... ')
    clientSocket.send(y.encode())

def receive():
    global placePiece
    while True:
        try:
            msg = clientSocket.recv(1024).decode()
            if "You're up." in msg:
                placePiece = True
            print(msg)
        except OSError:
            print("End")
            # Possibly client has left the chat.
            break

def send():  
    global placePiece
    while True:
        try:
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
    print("C1")
    clientSocket.send(NAME.encode())
    print("C2")

    # Start the receiving thread
    receive_thread = Thread(target=receive)
    print("C3")
    receive_thread.start()
    print("C4")
    # Start the sending thread
    send_thread = Thread(target=send)
    print("C5")
    send_thread.start()
    print("C6")

    # Wait for child threads to stop
    receive_thread.join()
    print("C7")
    send_thread.join()
    print("C8")
if __name__ == "__main__":
    main()