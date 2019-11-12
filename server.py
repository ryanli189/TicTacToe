from socket import *
import random

players = {}

def printLeaderboard:
    message = '''Top 10 Leaderboard:
    '''
    return message

def broadcast(player1, player2, message):
    player1.connectionSocket.send(message.encode())
    player2.connectionSocket.send(message.encode())

class Player:
    winCount = 0
    def __init__(self, name, connectionSocket):
        self.name = name
        self.connectionSocket = connectionSocket
    def addWin(self):
        self.winCount += 1

class Board:
    tiles = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
    
    def  __init__(self):
        pass
    def wipeBoard(self):
        tiles = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
    def placeX(self, x, y):
        if x < len(tiles) && y < len(tiles[0]):
            if tiles[x,y] = ' ':
                tiles[x,y] = X
                return True
        return False
    def placeO(self, x, y):
        if x < len(tiles) && y < len(tiles[0]):
            if tiles[x,y] = ' ':
                tiles[x,y] = X
                return True
        return False
    def printBoard(self):
        board = ''''''
        for i in range(len(tiles)):
            for j in range(len(tiles[0])):
                board += tiles[i,j]
                if j < len(tiles[0] - 1):
                    board += '|'
                else:
                    board += '\n'
            if i < len(tiles - 1):
                board += '------\n'
        return board

serverPort = 2019
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('The server is ready to receive')

connectionSocket, addr = serverSocket.accept()
name = connectionSocket.recv(1024).decode()
print(name +' has connected')
player[0] = Player(name, connectionSocket)

connectionSocket, addr = serverSocket.accept()
name = connectionSocket.recv(1024).decode()
print(name +' has connected')
player[1] = Player(name, connectionSocket)

message = player[0].name + ' vs. ' + player[1].name
broadcast(player[0], player[1], message)

isFirst = random.choice([0,1])
message = player[isFirst].name + ' is X and will go first. Other player is O and will go second.'
broadcast(player[0], player[1], message)

while True:
    
        

    message = connectionSocket1.recv(1024).decode()
    if "{quit}" in message:
        print(name1 + ' has left the chat.')
        exitMessage = name1 + " has left the chat."
        connectionSocket2.send(exitMessage.encode())
        break
    connectionSocket2.send(message.encode())
    message = connectionSocket2.recv(1024).decode()
    if "{quit}" in message:
        print(name2 + ' has left the chat.')
        exitMessage = name2 + " has left the chat."
        connectionSocket1.send(exitMessage.encode())
        break
    connectionSocket1.send(message.encode())
connectionSocket1.close()
connectionSocket2.close()
