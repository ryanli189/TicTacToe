from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

players = {}  #key socket, value Player

#Set up server
serverPort = 2019
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))

# All default messages
welcomeMsg = 'Welcome to TicTacToe! Please type your name and press enter.'
inQueueMsg = 'Please wait. Looking for another player.'
invalidMoveError = 'Error: invalid move. Choose a valid location.'
yourTurnMsg = "You're up. Choose a valid locaiton to place a piece."
endOptionMsg = 'Enter "Q" to quit. Enter "R" for a rematch.'

# TODO: adapt
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

def getMatchUpInfo():
    message = ''
    for sock in players:
        message += players[sock].name + ' (' + str(players[sock].winCount) + 'wins) vs. '
    return message[:-4]

def checkPlayersActive():
    for sock in players:
        if not players[sock].isActive:
            return False
    return True

def swapRoles():
    for sock in players:
        if players[sock].turnNum == 1:
            players[sock].goingSecond()
        elif players[sock].turnNum == 2:
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
        self.turnNum = 2
    def getTurn(self):
        if self.turnNum == 1:
            return 'Going first (X)'
        elif self.turnNum == 2:
            return 'Going second (O)'
        else:
            return 'Error! Turn number has not been picked yet.'

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
    def place(self, x, y, XorO):
        if XorO == 1:
            return self.placeX(x,y)
        elif XorO == 2:
            return self.placeO(x,y)
    def printBoard(self):
        return '--------\n' + '\n'.join([' '.join(['{:2}'.format(item) for item in row]) for row in self.tiles]) + '\n--------\n'
    def gameWon(self, playerNum):
        if playerNum == 1:
            token = 'X'
        elif playerNum == 2:
            token = 'O'
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

game = Board() # create game board

# Handles incomming connections
def accept_incoming_connections():
    i = 1
    while True:
        print(i)
        # Set up a new connection from the chat client
        client, client_address = serverSocket.accept()
        print("%s:%s has connected." % client_address)
        # Send welcome message
        client.send(welcomeMsg.encode())
        name = client.recv(1024).decode()
        players[client] = Player(name, client)
        # If only one player is connected thus far
        if len(players) == 1:
            players[client].goingFirst()
            print('Waiting for players')
            client.send(inQueueMsg.encode())
        if len(players) > 1:
            players[client].goingSecond()
            # Start client thread to handle the new connection
            Thread(target=playGame, args=(client,)).start()
        print(i, '.2')
        i += 1

def playGame(clientSocket):
    while True: #Runs thorugh the loop until server is shut down
        while checkPlayersActive(): #Runs through while loop until one or both players quit, this is a matchup loop
            # Set up for start of new game
            gameOver = False
            turnCounter = 1
            players[clientSocket].addGame()
            #Send game match up message to both players to start game
            broadcast(getMatchUpInfo())
            sendMessage(clientSocket, players[clientSocket].getTurn())
            while not gameOver: #Runs through while loop until current game ends, this is a game loop
                # If it is player's turn to play
                if turnCounter % players[clientSocket].turnNum == 0:
                    sendMessage(clientSocket, yourTurnMsg)
                    while True:
                        x = clientSocket.recv(1024).decode()
                        y = clientSocket.recv(1024).decode()
                        if game.place(x, y, players[clientSocket].turnNum):
                            break
                        sendMessage(clientSocket, invalidMoveError)
                    # Print board
                    broadcast(game.printBoard())
                    # If player won
                    if game.gameWon(players[clientSocket].turnNum):
                        gameOver = True
                        players[clientSocket].addWin()
                        broadcast('\nGame over. ' + players[clientSocket].name + ' wins.')
                        if players[clientSocket].turnNum == 1:
                            swapRoles()
                turnCounter += 1

            #Option to end
            broadcast(endOptionMsg)
            response = clientSocket.recv(1024).decode()
            if 'Q' in response:
                players[clientSocket].quit()
                players[clientSocket].connectionSocket.close()

def main():
    serverSocket.listen(1)
    print('The server is ready to receive')

    acceptThread = Thread(target=accept_incoming_connections)
    acceptThread.start()
    acceptThread.join()

    serverSocket.close()

if __name__ == "__main__":
    main()