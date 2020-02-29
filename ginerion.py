#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from enum import Enum

import threading
import time
import random

##############################################################################
# Game grid setup
imax = 4
jmax = 4
grid=[]
for i in range(0,imax):
    grid.append([])
    for j in range(0,jmax):
        grid[i].append(' ')

###############################################################################
def gridIsFull():
    global grid,imax,jmax
    for i in range(0,imax):
        for j in range(0,jmax):
            if grid[i][j]==' ':
                return False
    return True

###############################################################################
def printGrid():
    global grid,imax
    print
    for i in range(0,imax):
        print (grid[i])

###############################################################################
def stealPawns(i, j, pName):
    global grid, imax, jmax
    pawn = grid[i][j]
    otherPawn = 'O' if pawn == 'X' else 'X'

    # Check the 4 pawns opposite to the one just added at (i,j),
    #  and steal the pawns in between if the symbols match
    if i < imax - 2 and grid[i + 2][j] == pawn and grid[i + 1][j] == otherPawn:
        grid[i + 1][j] = pawn
        print(pName + " has stolen pawn " + otherPawn + " at " \
              + "[" + str(i + 1) + ", " + str(j) + "]!!!")

    if i > 1 and grid[i - 2][j] == pawn and grid[i - 1][j] == otherPawn:
        grid[i - 1][j] = pawn
        print(pName + " has stolen pawn " + otherPawn + " at " \
              + "[" + str(i - 1) + ", " + str(j) + "]!!!")

    if j < jmax - 2 and grid[i][j + 2] == pawn and grid[i][j + 1] == otherPawn:
        grid[i][j + 1] = pawn
        print(pName + " has stolen pawn " + otherPawn + " at " \
              + "[" + str(i) + ", " + str(j + 1) + "]!!!")


    if j > 1 and grid[i][j - 2] == pawn and grid[i][j - 1] == otherPawn:
        grid[i][j - 1] = pawn
        print(pName + " has stolen pawn " + otherPawn + " at " \
              + "[" + str(i) + ", " + str(j - 1) + "]!!!")

###############################################################################
class Player(threading.Thread):

    def __init__(self, name, num, pawn, playerType):
        threading.Thread.__init__(self)
        self.setName(name)  # Player name (e.g., 'Player 1')
        self.num = num  # player id (e.g., 1 for Player 1)
        self.pawn = pawn  # Type of pawn assigned to the player
        self.playerType = playerType  # player type: 0 = computer, 1 = human
        self.stop = False  # Flag used to stop the thread when requested by the main loop

    def run(self):
        # Grant access to global variables
        global mutex # lock on concurrent access to global variables
        global readyToPlay  # Flag granted authorization to play to the players
        global moveCounter  # move counter
        global first  # id of the player playing first
        global nbjoueurs  # total number of playes
        # global aide  # dit si l'affichage d'une aide est demandé

        while not self.stop:  # While thread has not been stopped by game loop

            ##### => each player awaits to its turn
            while True: # Player wait loop
                # acquire lock on global variables
                mutex.acquire()
                if self.stop:
                    # Game over, leave player wait loop but keeping the acquired lock
                    break
                if readyToPlay and (moveCounter+first)%nbPlayers == self.num:
                    # = it is this player's turn to play, keep lock and leave loop
                    break
                # otherwise, release lock and let other players check for their turn
                mutex.release()

            ##### => Current player's turn

            if not self.stop:
                if self.pawn == 'X':
                    otherPawn = 'O'
                else:
                    otherPawn = 'X'
                    print
                    print(self.getName() + " plays ('" + self.pawn + "' against '" + otherPawn + "')")

                if self.playerType == PlayerType.COMPUTER:
                    # Player is a computer

                    # self.chx = ajouer(self.pion)
                    # print self.getName() + " joue case: ",self.chx
                    # grille[self.chx[0]][self.chx[1]]=self.pion
                    time.sleep(0.1)
                else:
                    # Player is a human
                    # self.chx = ajouer(self.pion)
                    ch=self.getName() + " plays cell (e.g., '[0,2]'): "
                    while True:
                        self.move = input(ch)
                        try:
                            # player has entered a line, column couple
                            x = eval(self.move)
                            if ((type(x) == list or type(x) == tuple) and len(x) == 2) \
                               and (0 <= x[0] < imax) and (0 <= x[1] < jmax) \
                               and grid[x[0]][x[1]] == ' ':
                                grid[x[0]][x[1]] = self.pawn
                                # Perform stealing checks and update grid
                                stealPawns(x[0], x[1], self.getName())
                                break
                            else:
                                raise Exception()
                        except:
                            # ici, le choix entré n'est pas correct
                            print("--> incorrect move. FORMAT: 'line, col' or '[line, col]'")
                            pass

            ##### => end of player turn

            # execution is yielded back to game loop
            readyToPlay = False

            # Release mutex on global variables
            mutex.release()

            # If termination has been requested, terminate
            if self.stop:
                break

    def terminate(self):
        self.stop = True

###############################################################################
nbPlayers = 2

class PlayerType(Enum):
    COMPUTER = 0,
    HUMAN = 1

# Player types: 0=ordinateur, 1=humain; there must be: len(playerTypes) == nbPlayers
while True:
    print
    print (u"Game type:")
    print (u"[1]: 2 humans play together")
    print (u"[2]: 1 computer plays against 1 human player")
    print (u"[3]: the computer plays against itself")
    x = input("What type of game do you wish to play? [1 by default]: ")
    if x == '1' or x == '':
        playerTypes = [1,1]
        break

    if x == '2':
        playerTypes = [0,1]
        print('Games with computer are not supported yet.')
        exit()

    if x == '3':
        playerTypes = [0,0]
        print('Games with computer are not supported yet.')
        exit()

# Assign a pawn type to each player
pawns = ['O','X']
print
print (u"=====> player 1 has the 'O' pawn, the other the 'X' pawn")


# define the player who will play the first move, or choose randomly
while True:
    print
    print (u"Who should play the first move?")
    print (u"[1] player 1 starts")
    print (u"[2] player 2 starts")
    print (u"[3] choose randomly")
    x = input(u"Choose an option [3 by default]: ")
    if x == '1':
        first = 0
        break
    elif x == '2':
        first = 1
        break
    elif x == '3' or x == '':
        first = random.randint(0, nbPlayers - 1)
        break

print
print ("=====> Player " + str(first+1) + " plays first")

############################## => program initialization

# mutex on global variables below
mutex = threading.Lock()

# Counts the number of moves played by all players,
moveCounter = -1

# Flag used to yield back the execution to the main program after a move is played
readyToPlay = False

# Creation of the list of players
players = []
for i in range(0,nbPlayers):
    p = Player("Player %d" % (i+1), i, pawns[i], playerTypes[i])
    p.setDaemon(True)
    players.append(p)

# lancement de tous les threads des joueurs
for i in range(0, nbPlayers):
    players[i].start()

# ##############################
# # Game loop

t = time.time()
while True:
    # waiting for a player to play its turn
    while True:
        mutex.acquire()
        if not readyToPlay:
            moveCounter +=1 #  increment move counter for the move has just been played
            break
        mutex.release()

    # print the updated game grid
    printGrid()

    # end of game condition
    if gridIsFull():
        print
        mutex.release()
        break

    # New round detection
    roundNum = (moveCounter / nbPlayers) + 1
    nextPlayer = moveCounter % nbPlayers
    if nextPlayer == 0:
        print
        print (u"=====> Starting round #" + str(roundNum))

    # Allow the next player to play its turn
    readyToPlay = True
    mutex.release()
    # loop until the next player has made his move

#############################
# Game end
print
print ("Game over!")

# stop all threads
for i in range(0, nbPlayers):
    players[i].terminate()

# Wait until all threads are terminated
for i in range(0, nbPlayers):
    players[i].join()
    mutex.acquire()
    print ("end of thread " + players[i].getName())
    mutex.release()


print
print (u"Come back soon for another game of Ginerion!")

printGrid()
