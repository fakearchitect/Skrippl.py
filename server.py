#!/usr/local/bin/python
# coding: utf-8
import random
import socket
import select
import os

def senBlirAlltSvart(): # Clears the screen on Linux, Mac & Win.
    if (os.name == "posix"): os.system("clear")
    elif (platform.system() == "Windows"): os.system("cls")
    else: pass

connections = []
playerNames = {}
buffer = 1024
serverIP = "127.0.0.1"
port = random.randrange(9000,9999)
serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSock.bind((serverIP, port))
serverSock.listen(15)
connections.append(serverSock)
global addr
global theWord

senBlirAlltSvart()

print(f"The game server is now live at {serverIP} on port {port}")


def newWord():
    # The first line here is a supposedly relible way of getting the absolute path to this script.
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, "nouns.txt")) as wordFile:
        wordList = wordFile.readlines()
    return wordList[random.randrange(0,len(wordList))]
theWord = newWord()



def wordIsCorrect(msgValue):
    global theWord
    # Making it case-insensitive and eliminating trailing whitspace
    msgValue = msgValue.strip().upper().lower()
    theWord = theWord.strip().upper().lower()
    if msgValue == theWord:
        return True
    else:
        return False

def msgInterpreter(data,sock):
    # Incoming messages from the game client are structured differently depending on their purpose.
    # Common for most of them is the inclusion of "//" as a data divider. I originally chose those
    # chars because I wanted the ability for players to chat with each other, starting the msg with //.
    # A msg containing just a word is treated as a word guess.
    # The server responds with messages divided in sections by colons.
    msgParts = data.decode().strip().split("//")
    if len(msgParts) == 2: # All message types, except for Word Guesses, are made out of 2 elements.
        msgType = msgParts[0]
        msgTypeLength = len(msgType)
        msgValue = msgParts[1]

        if msgTypeLength < 1:
            msgType = "//"
            print(f"Msg recognized as chat message from player {playerNames[sock.fileno()]}")
            data = str(msgType+":"+str(playerNames[sock.fileno()])+":"+str(msgValue).strip())
            if msgValue == "Ooooooh! I can see it now!":
                data = str("CH:"+str(playerNames[sock.fileno()])+":"+theWord)
            data = data.encode()

        if msgType == "SN":
            print("Msg recognized as Set Name command)")
            playerNames[sock.fileno()] = msgValue
            totPlayers = len(playerNames)
            print(f"Received player name for player ID {sock.fileno()}: {playerNames[sock.fileno()]}")
            broadcast(sock, "{} has joined the game, making you a total of {} people!".format(msgValue, totPlayers))

        if msgType == "CO":
            print(f"Msg recognized as paint data from player {playerNames[sock.fileno()]}: {msgValue}")
            data = str("CO:"+str(playerNames[sock.fileno()])+":"+str(msgValue))
            data = data.encode()

    elif len(msgParts) == 1:
        # The lack the split divider "//" indicates this is a word guess.
        msgType = "GS"
        msgValue = data.decode()
        print(f"Msg recognized as word guess from player {playerNames[sock.fileno()]}")
        if wordIsCorrect(msgValue):
            data = (str("RG:" + playerNames[sock.fileno()] + ":" + msgValue)).encode()
            print(playerNames[sock.fileno()] + " guessed right!")
        else:
            data = (str("GS:" + playerNames[sock.fileno()] + ":" + msgValue)).encode()
            print(playerNames[sock.fileno()] + " guessed wrong.")
    else:
        print("Msg was not recognized.")
    return data


def broadcast(sock, msg, addr=None):
    for s in connections:
        if s != sock and s != serverSock:
            try:
                s.send(msg.encode('utf8'))
            except:
                s.close()
                connections.remove(s)


while True:
    readsock, writesock, errsock = select.select(connections, [], [])
    for sock in readsock:
        if sock == serverSock:
            sockfd, addr = serverSock.accept()
            #print("Sockfd",sockfd)
            connections.append(sockfd)
            print(" {} connected".format(addr))
        else:
            try:
                data = sock.recv(buffer)
                if data:
                    info = msgInterpreter(data,sock)
                    sock.send(info)
                    broadcast(sock, info.decode(), addr)
            except:
                goodBye = str("Player " + str(playerNames[sock.fileno()]) + " has left the game.")
                playerNames.pop(sock.fileno(), None)
                #broadcast(sock, goodBye.encode())
                print(goodBye)
                sock.close()
                connections.remove(sock)
                continue
serverSock.close()
