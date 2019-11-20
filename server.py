from socket import *
import random

players = []  #list containing all PLayer objects

welcomeMsg = 'Welcome to TicTacToe! Please type your name and press enter.'
inQueueMsg = 'Please wait. Looking for another player.'
invalidMoveError = 'Error: invalid move. Choose a valid location.'
yourTurnMsg = "You're up. Choose a valid locaiton to place a piece."
endOptionMsg = 'Enter "Q" to quit. Enter "R" for a rematch.'

def printLeaderboard():
    message = '''Top 10 Leaderboard:
    Name | Win Count | Game Count
    '''
    #Sort by win number
    sortedPlayers = sorted(players, key = lambda player: player.winCount)
    
    #Find if number of players is less than 10
    leaderboardCount = 10
    if sortedPlayers.count() < 10:
        leaderboardCount = sortedPlayers.count()
    
    for i in range(leaderboardCount):
        message += sortedPlayers[i].name + ' | ' + sortedPlayers[i].winCount + ' | ' + sortedPlayers[i].gameCount + '\n'
    return message

#Send message to player
def sendMessage(connectionSocket, message):
    connectionSocket.send(message.encode())
    #connectionSocket.send(message.encode())

#Send message to player 1 and player 2
def broadcast(player1, player2, message):
    sendMessage(player1.connectionSocket, message)
    sendMessage(player2.connectionSocket, message)

#Used to keep track of player name, wins, and connection socket
class Player:
    def __init__(self, name, connectionSocket):
        self.name = name
        self.connectionSocket = connectionSocket
        self.winCount = 0
        self.gameCount = 0
    def addWin(self):
        self.winCount += 1
    def addGame(self):
        self.gameCount += 1

#Game board: new board, place x or o, print board out
class Board:
    def  __init__(self):
        self.wipeBoard()
    def wipeBoard(self):
        self.tiles = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
    def placeX(self, x_string, y_string):
        x = int(x_string)
        y = int(y_string)
        if x < len(self.tiles) and y < len(self.tiles):
            if self.tiles[y][x] == '-':
                self.tiles[y][x] = 'X'
                return True
        return False
    def placeO(self, x_string, y_string):
        x = int(x_string)
        y = int(y_string)
        if x < len(self.tiles) and y < len(self.tiles):
            if self.tiles[y][x] == '-':
                self.tiles[y][x] = 'O'
                return True
        return False
    def printBoard(self):
        # board = '''------
        # '''
        # for i in range(len(self.tiles)):
        #     for j in range(len(self.tiles[0])):
        #         board += self.tiles[i][j]
        #         if j < len(self.tiles[0]) - 1:
        #             board += '|'
        #         else:
        #             board += '\n'
        #     if i < len(self.tiles) - 1:
        #         board += '------\n'
        # return board
        return '--------\n' + '\n'.join([' '.join(['{:2}'.format(item) for item in row]) for row in self.tiles]) + '\n--------\n'
    def gameWon(self, token):
        #Check horizontal
        for i in range(len(self.tiles)):
            if self.tiles[i][0] == token and self.tiles[i][1] == token and self.tiles[i][2] == token:
                return True
        #Check veritical
        for i in range(len(self.tiles[0])):
            if self.tiles[0][i] == token and self.tiles[1][i] == token and self.tiles[2][i] == token:
                return True
        #Check diagonal
        if self.tiles[0][0] == token and self.tiles[1][1] == token and self.tiles[2][2] == token:
            return True
        if self.tiles[0][2] == token and self.tiles[1][1] == token and self.tiles[2][0] == token:
            return True
        return False
#Set up server
serverPort = 2019
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('The server is ready to receive')

#Get first client/player
#connectionSocket, addr = serverSocket.accept()
#sendMessage(connectionSocket, welcomeMsg)
#name = connectionSocket.recv(1024).decode()
#print(name +' has connected')
#players[0] = Player(name, connectionSocket)
#sendMessage(connectionSocket, inQueueMsg)

#Get second client/player
#connectionSocket, addr = serverSocket.accept()
#sendMessage(connectionSocket, welcomeMsg)
#name = connectionSocket.recv(1024).decode()
#print(name +' has connected')
#players[1] = Player(name, connectionSocket)

print('Waiting for players')
i = 0
while True:
    connectionSocket, addr = serverSocket.accept()
    sendMessage(connectionSocket, welcomeMsg)
    name = connectionSocket.recv(1024).decode()
    players.append(Player(name, connectionSocket))
    if i == 1:
        break
    print(name +' has connected. Waiting for 1 more players to join')
    sendMessage(connectionSocket, inQueueMsg)
    i += 1

#Send game match up message to both players
message = players[0].name + ' (' + str(players[0].winCount) + ' wins) vs. ' + players[1].name + ' (' + str(players[0].winCount) + ' wins)'
broadcast(players[0], players[1], message)

game = Board()

#TODO OPTIONAL make this and the previous able to be implemented with more users
#TODO Mechanism for saving and loging people back in
p1 = 0
p2 = 1

while True: #Runs through while loop until one or both players quit
    gameOver = False
    message = players[p1].name + ' is first (X). ' + players[p2].name + ' is second (O).\n'
    broadcast(players[p1], players[p2], message)

    turnCounter = 0
    while not gameOver: #Runs through while loop until current game ends
        #Add game to each player's record
        players[p1].addGame()
        players[p2].addGame()

        if turnCounter % 2 == 0:
            #Player 1 inputs moves until valid move
            sendMessage(players[p1].connectionSocket, yourTurnMsg)
            while True:
                p1_x = players[p1].connectionSocket.recv(1024).decode()
                p1_y = players[p1].connectionSocket.recv(1024).decode()
                print("Coordinates: " + p1_x + " and " + p1_y)
                if game.placeX(p1_x, p1_y): #If placed on valid location move on
                    break
                #If not place on valid location send error message and repeat
                sendMessage(players[p1].connectionSocket, invalidMoveError)
            if game.gameWon('X'):
                gameOver = True
                players[p1].addWin()
                message = 'Game Over. ' + players[p1].name + ' wins.'
                broadcast(players[p1], players[p2], message)

                #First player will now go second
                temp = p1
                p1 = p2
                p2 = p1
        else:
            #Player 2 inputs moves until valid move
            sendMessage(players[p2].connectionSocket, yourTurnMsg)
            while True:
                p2_x = players[p2].connectionSocket.recv(1024).decode()
                p2_y = players[p2].connectionSocket.recv(1024).decode()
                if game.placeO(p2_x, p2_y): #If placed on valid location move on
                    break
                #If not place on valid location send error message and repeat
                sendMessage(players[p2].connectionSocket, invalidMoveError)
            if game.gameWon('O'):
                gameOver = True
                players[p2].addWin()
                message = 'Game Over. ' + players[p2].name + ' wins.'
                broadcast(players[p1], players[p2], message)
        
        turnCounter += 1
        #Print new board
        broadcast(players[p1], players[p2], game.printBoard())

    #Option to end
    broadcast(players[p1], players[p2], endOptionMsg)
    p1Response = players[p1].connectionSocket.recv(1024).decode()
    p2Response = players[p2].connectionSocket.recv(1024).decode()
    if 'Q' in p1Response:
        players[p1].connectionSocket.close()
    if 'Q' in p2Response:
        players[p2].connectionSocket.close()
    if 'Q' in p1Response or 'Q' in p2Response:
        break