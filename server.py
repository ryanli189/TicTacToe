from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys

players = {}  #key socket, value Player
turnCounter = 0
gameOver = False
#Set up server
serverPort = 2019
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))

# All default messages
welcomeMsg = 'Welcome to TicTacToe! Please type your name and press enter.'
inQueueMsg = 'Please wait. Looking for another player.'
invalidMoveError = 'Error: invalid move. Choose a valid location.'
yourTurnMsg = "You're up. Choose a valid locaiton to place a piece."
endOptionMsg = 'Enter "Q" to quit. Enter "R" (or any other character) for rematch.'

def getMatchUpInfo():
    message = ''
    for sock in players:
        message += players[sock].name + ' (' + str(players[sock].winCount) + ' wins) vs. '
    message += message[:-4] + '\n'
    return message

def checkPlayersActive():
    for sock in players:
        if not players[sock].isActive:
            return False
    return True

def swapRoles():
    for sock in players:
        if players[sock].turnNum == 1:
            players[sock].goingSecond()
        elif players[sock].turnNum == 0:
            players[sock].goingFirst()

#Send message to player
def sendMessage(connectionSocket, message):
    connectionSocket.send(message.encode())

# Broadcasts a message to all the clients
def broadcast(msg):
    for sock in players:
        sock.send(msg.encode())

# Broadcasts a message to all the clients, using prefix for name identification
def broadcastChat(msg, prefix=""):
    for sock in players:
        sock.send(prefix.encode("utf8")+msg)

#Used to keep track of player name, wins, and connection socket
class Player:
    turnNum = 0
    winCount = 0
    gameCount = 0
    name = ''
    def __init__(self, name, connectionSocket):
        self.name = name
        self.connectionSocket = connectionSocket
        self.isActive = True
    def addWin(self):
        self.winCount += 1
    def addGame(self):
        self.gameCount += 1
    def quit(self):
        self.isActive = False
    def rejoin(self):
        self.isActive = True
    def goingFirst(self):
        self.turnNum = 1
    def goingSecond(self):
        self.turnNum = 0
    def getTurn(self):
        if self.turnNum == 1:
            return 'Going first (X)\n'
        elif self.turnNum == 0:
            return 'Going second (O)\n'
        else:
            return 'Error! Turn number has not been picked yet.\n'

#Game board: new board, place x or o, print board out
class Board:
    def  __init__(self):
        self.wipeBoard()
    def wipeBoard(self):
        self.placementTiles = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
    def placeX(self, x, y):
        # x = int(x_string)
        # y = int(y_string)
        if x < len(self.placementTiles) and y < len(self.placementTiles):
            if self.placementTiles[y][x] != 'O' and self.placementTiles[y][x] != 'X':
                self.placementTiles[y][x] = 'X'
                return True
        return False
    def placeO(self, x, y):
        # x = int(x_string)
        # y = int(y_string)
        #print("Checkpoint 3")
        if x < len(self.placementTiles) and y < len(self.placementTiles):
            #print("Checkpoint 4")
            if self.placementTiles[y][x] != 'O' and self.placementTiles[y][x] != 'X':
                self.placementTiles[y][x] = 'O'
                return True
        return False
    def place(self, loc, XorO):
        # Corrolate location with coordinates
        loc = int(loc)
        if loc == 1 or loc == 4 or loc == 7:
            x = 0
        elif loc == 2 or loc == 5 or loc == 8:
            x = 1
        elif loc == 3 or loc == 6 or loc == 9:
            x = 2
        else:
            return False
        #print("Checkpoint 1")
        if loc == 1 or loc == 2 or loc == 3:
            y = 0
        elif loc == 4 or loc == 5 or loc == 6:
            y = 1
        elif loc == 7 or loc == 8 or loc == 9:
            y = 2
        #print("Checkpoint 2,, loc (" + str(loc) + "), x (" + str(x) + "), y (" + str(y) + ")")
        # Place proper piece, X or Y
        if XorO == 1:
            return self.placeX(x,y)
        elif XorO == 0:
            return self.placeO(x,y)
    def printPlacementBoard(self):
        return '--------\n' + '\n'.join([' '.join(['{:2}'.format(item) for item in row]) for row in self.placementTiles]) + '\n--------\n'
    def gameWon(self, playerNum):
        if playerNum == 1:
            token = 'X'
        elif playerNum == 0:
            token = 'O'
        #Check horizontal
        for i in range(len(self.placementTiles)):
            if self.placementTiles[i][0] == token and self.placementTiles[i][1] == token and self.placementTiles[i][2] == token:
                return True
        #Check veritical
        for i in range(len(self.placementTiles[0])):
            if self.placementTiles[0][i] == token and self.placementTiles[1][i] == token and self.placementTiles[2][i] == token:
                return True
        #Check diagonal
        if self.placementTiles[0][0] == token and self.placementTiles[1][1] == token and self.placementTiles[2][2] == token:
            return True
        if self.placementTiles[0][2] == token and self.placementTiles[1][1] == token and self.placementTiles[2][0] == token:
            return True
        return False

game = Board() # create game board

# Handles incomming connections
def accept_incoming_connections():
    while True:
        # Set up a new connection from the chat client
        client, client_address = serverSocket.accept()
        # Send welcome message
        client.send(welcomeMsg.encode())
        name = client.recv(1024).decode()
        players[client] = Player(name, client)
        print(name + " (%s:%s) has connected." % client_address)
        # If only one player is connected thus far
        if len(players) == 1:
            players[client].goingFirst()
            print('Waiting for players')
            client.send(inQueueMsg.encode())
        if len(players) > 1:
            players[client].goingSecond()
            # Start client thread for each client to handle the new connection
            for aClient in players:
                Thread(target=playGame, args=(aClient,)).start()

def playGame(clientSocket):
    while checkPlayersActive(): #Runs through while loop until one or both players quit, this is a matchup loop
        # Set up for start of new game
        global turnCounter
        global gameOver
        turnCounter = 1
        gameOver = False
        players[clientSocket].addGame()
        game.wipeBoard()
        #Send game match up message to both players to start game
        sendMessage(clientSocket, getMatchUpInfo())
        sendMessage(clientSocket, players[clientSocket].getTurn())
        #Print template board for first player
        if players[clientSocket].turnNum == 1:
            sendMessage(clientSocket, game.printPlacementBoard())
        while not gameOver: #Runs through while loop until current game ends, this is a game loop
            if turnCounter % 2 == players[clientSocket].turnNum:
                sendMessage(clientSocket, yourTurnMsg)
                #sendMessage(clientSocket, game.printPlacementBoard())
                while True:
                    loc = clientSocket.recv(1024).decode()
                    if game.place(loc, players[clientSocket].turnNum):
                        break
                    sendMessage(clientSocket, invalidMoveError)
                # Print board
                broadcast( game.printPlacementBoard())
                # If player won
                if game.gameWon(players[clientSocket].turnNum):
                    gameOver = True
                    players[clientSocket].addWin()
                    broadcast('\nGame over. ' + players[clientSocket].name + ' wins.')
                    if players[clientSocket].turnNum == 1:
                        swapRoles()
                turnCounter += 1

        #Option to end
        sendMessage(clientSocket, endOptionMsg)
        response = clientSocket.recv(1024).decode()
        if 'Q' in response:
            players[clientSocket].quit()
            name = players[clientSocket].name
            print(name + ' has quit.')
            msg = name + ' has quit. Ending game.'
            broadcast(msg)
            sys.exit()
            break

def main():
    serverSocket.listen(1)
    print('The server is ready to receive')

    acceptThread = Thread(target=accept_incoming_connections)
    acceptThread.start()
    acceptThread.join()
    serverSocket.close()

if __name__ == "__main__":
    main()