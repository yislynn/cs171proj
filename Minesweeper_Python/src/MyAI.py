# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================
import random

from AI import AI
from Action import Action


class MyAI(AI):

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        self.__rows = rowDimension
        self.__cols = colDimension
        self.__totalMines = totalMines
        self.__currX = startX
        self.__currY = startY
        self.__numCovered = (self.__rows * self.__cols) - self.__totalMines
        # int label, negative = covered, 0-8 = label (uncovered)
        
        # -1 means covered
        # -2 means flagged
        # -3 means safe
        # -4 means flagged in game
        self.__board = [[-1 for c in range(colDimension)] for r in range(rowDimension)]

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

    def getAction(self, number: int) -> "Action Object":
        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        # update board
        self.__board[self.__currX][self.__currY] = number
        # check if we're done
        # if number of mines is M, and M mines have been identified (on board), 
        # all other covered tiles are safe. (may need to be implemented if this skip causes issues)
        if self.__numCovered == self.__totalMines:
            return Action(AI.Action.LEAVE)
        # figure out UNCOVER(X,Y)
        neighbors = self.getNeighbors(self.__currX, self.__currY)
        
        # todo: try simple rule of thumb
        # uncover all neighbors if 0
        
        # logic rules
        # 1. if tile = number N and has N flagged (-2) neighbors, all uncertain (-1) neighbors are safe; 
        # change to "safe" on board (-3)
        # 2. if tile = number N and has N uncertain (-1) neighbors, all those neighbors are mines (-2)
        uncertain = list(filter(lambda ne: (self.__board[ne[0]][ne[1]] == -1), neighbors))
        flagged = list(filter(lambda ne: (self.__board[ne[0]][ne[1]] == -2 or self.__board[ne[0]][ne[1]] == -4), neighbors))

        if (number == len(flagged)):
            for x, y in uncertain:
                self.__board[x][y] = -3
        elif (number == len(uncertain)):
            for x, y in uncertain:
                self.__board[x][y] = -2

        # actions
        flagged = self.getFlagged()
        if len(flagged) != 0:
            # check for tiles that are found to have mines; flag on board
            self.__board[flagged[0][0]][flagged[0][1]] = -4
            return Action(AI.Action.FLAG, flagged[0][0], flagged[0][1])
        else:
            # check if there are any safe tiles (-3)
            # pick one of the safe tiles to do
            safe = self.getSafe() # get a safe tile to process
            if len(safe) != 0: # if there exists at least one safe tile, uncover
                #print("Choosing Safe Tile")
                #self.__board[safe[0][0]][safe[0][1]] = 0
                self.__currX = safe[0][0]
                self.__currY = safe[0][1]
                self.__numCovered -= 1 # decrement covered count
                return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1])
            else:
                # re evaluate to find safe tiles
                for i in range(self.__rows):
                    for j in range(self.__cols):
                        if self.__board[i][j] >= 0:
                            neighbors = self.getNeighbors(i, j)
                            uncertain = list(filter(lambda ne: (self.__board[ne[0]][ne[1]] == -1), neighbors))
                            flagged = list(filter(lambda ne: (self.__board[ne[0]][ne[1]] == -2 or self.__board[ne[0]][ne[1]] == -4), neighbors))
                            if (self.__board[i][j] == len(flagged)):
                                for x, y in uncertain:
                                    self.__board[x][y] = -3
                            elif (self.__board[i][j] == len(uncertain)):
                                for x, y in uncertain:
                                    self.__board[x][y] = -2
                # get any newly generated safe tiles, if possible
                safe = self.getSafe() # get a safe tile to process
                if len(safe) != 0: # if there exists at least one safe tile, uncover
                    self.__currX = safe[0][0]
                    self.__currY = safe[0][1]
                    self.__numCovered -= 1 # decrement covered count
                    return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1])
                        
                else:
                    # no known safe tiles exist
                    idk = self.getUncertain() # get unknown tile to process
                    if len(idk) != 0: # if there exists at least one unknown tile
                        #print("Choosing Uncertain Tile")
                        rand = random.choice(idk) # randomly choose a tile to uncover
                        self.__currX = rand[0]
                        self.__currY = rand[1]
                        self.__numCovered -= 1 # decrement covered count
                        return Action(AI.Action.UNCOVER, rand[0], rand[1])
                    else: # there are no unknown tiles = all tiles are uncovered = game is won = leave
                        return Action(AI.Action.LEAVE)

        # if number == 0:
        #     for n in neighbors:
        #         # uncover if covered
        #         if self.__board[n[0], n[1]] == -1:
        #             return Action(Action.UNCOVER, n[0], n[1])
 
        # if number == 1:
        #     uncovered = list(filter(lambda ne: (self.__board[ne[0]][ne[1]] == -1), neighbors))
        #     rand_uncover = random.choice(uncovered)
        #     return Action(Action.UNCOVER, rand_uncover[0], rand_uncover[1])
        
        # check # of uncovered neighbors
        # if # uncovered = 0, make random guess
        # if nonzero,
        # flag all if label == unmarked neighbors

        # if doesn't work, use better logic
        # if doesn't work, use EVEN BETTER logic

        # if uncover, decrement numCovered
    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

    def getNeighbors(self, x, y):
        neighbors = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                     (x, y - 1), (x, y + 1),
                     (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]
        ne = []
        for n in neighbors:
            # check if in bounds
            if n[1] < self.__cols and n[1] >= 0 and n[0] < self.__rows and n[0] >= 0:
                ne.append(n)
            # check if covered
        return ne

    def getSafe(self):
        safe = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j] == -3:
                    safe.append((i, j))
        return safe
    
    def getUncertain(self):
        idk = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j] == -1:
                    idk.append((i, j))
        return idk

    def getFlagged(self):
        flags = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j] == -2:
                    flags.append((i, j))
        return flags
