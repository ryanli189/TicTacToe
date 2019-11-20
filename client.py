from socket import *

#Make move
def play(clientSocket):
    x = input('Enter column number (0, 1, or 2) 0 being the left most column\n... ')
    clientSocket.send(x.encode())
    y = input('Enter row number (0, 1, or 2) 0 being the top most row\n... ')
    clientSocket.send(y.encode())
    message = clientSocket.recv(1024).decode()
    print(message)
    return message

#Set up client
serverName = '192.168.0.6'
serverPort = 2019
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

print(clientSocket.recv(1024).decode()) #Receive initial welcome message
name = input('... ') #Input username
clientSocket.send(name.encode())

message = clientSocket.recv(1024).decode()
print(message)
if 'Please wait' in message: #If first player to join wait for second and then recieve matchup information
    print(clientSocket.recv(1024).decode())

while True: #Matchup simulation
    gameRoundInfo = clientSocket.recv(1024).decode()
    print(gameRoundInfo) #Print game round information

    #If going second
    if (name + ' is second') in gameRoundInfo:
        print("Going second")
        print(clientSocket.recv(1024).decode()) #Print other player's move

    while True: #Game simulation
        #Play
        print("C1")
        #print(clientSocket.recv(1024).decode())
        print("Should be playing now")
        message = play(clientSocket)
        while 'Error' in message:
            message = play(clientSocket)
        
        #Watch
        message = clientSocket.recv(1024).decode()
        print(message)
        if 'Game Over' in message:
            print(clientSocket.recv(1024).decode())
            break

clientSocket.close