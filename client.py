#! /bin/python

from socket import *

serverName = '10.220.66.211'
serverPort = 2019
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
name = input('Welcome to NP chatroom! Please type your name and press enter...  ')
clientSocket.send(name.encode())
print('Hello ' + name + '! If you ever want to quit, type {quit} to exit.')

while True:
    otherMessage = clientSocket.recv(1024)
    print(otherMessage.decode())
    message = input()
    message = name + ': ' + message
    clientSocket.send(message.encode())
    if '{quit}' in message:                                                                                                  break
clientSocket.close
