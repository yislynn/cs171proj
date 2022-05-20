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
from operator import add
import random
from webbrowser import get
#from sys import set_coroutine_origin_tracking_depth

from AI import AI
from Action import Action


class MyAI(AI):
    class __Tile():
        def __init__(self) -> None:
            self.covered = True
            self.flag = False
            self.safe = False
            self.label = -1
            self.elabel = -1
        
        def __str__(self):
            return f"L:{self.label}/EL:{self.elabel}/S:{self.safe}/F:{self.flag}"


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
        self.__frontier = [(startX, startY)]
        # int label, negative = covered, 0-8 = label (uncovered)
    
        self.__board = [[self.__Tile() for c in range(colDimension)] for r in range(rowDimension)]

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

    def getAction(self, number: int) -> "Action Object":

        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        # update board
        if(number >= 0): self.__numCovered = self.__numCovered - 1
        tile = self.__board[self.__currX][self.__currY]
        tile.label = number
        tile.covered = False

        # update frontier
        if not self.__frontier.__contains__((self.__currX, self.__currY)):
            self.__frontier.append((self.__currX, self.__currY))

        # check if we're done
        # if number of mines is M, and M mines have been identified (on board), 
        # all other covered tiles are safe. (may need to be implemented if this skip causes issues)
        if self.__numCovered == self.__totalMines:
            return Action(AI.Action.LEAVE)

        # figure out UNCOVER(X,Y)
        flagged = self.get_flagged_neighbors(self.__currX, self.__currY)
        uncertain = self.get_covered_neighbors(self.__currX, self.__currY);        

        # 1. if tile = number N and has N flagged (-2) neighbors, all uncertain, neighbors are safe; 
        # change to "safe" on board
        if (number == len(flagged)):
            for x, y in uncertain:
                self.__board[x][y].safe = True
            # all neighbors either flagged or uncovered = tile no longer in frontier
            self.__frontier.remove((self.__currX, self.__currY)) 
        # 2. if tile = number N and has N uncertain (-1) neighbors, all those neighbors are mines (-2)
        elif (number == len(uncertain)):
            for x, y in uncertain:
                self.__board[x][y].flag = True
            # all neighbors either flagged or uncovered = tile no longer in frontier
            self.__frontier.remove((self.__currX, self.__currY)) 
        
        # update effective labels
        self.update_elabels(self.__currX, self.__currY)
        # get frontier, uncovered unflagged neighbors are safe if elabels are zero
        for f in self.__frontier:
            tile = self.__board[f[0]][f[1]]
            if tile.elabel == 0:
                for n in self.get_uncovered_neighbors[f[0]][f[1]]:
                    self.__board[n[0]][n[1]].safe = True
        
        # actions
        # check if there are any safe tiles
        # pick one of the safe tiles to do
        safe = self.get_safe() # get a safe tile to process
        if len(safe) != 0: # if there exists at least one safe tile, uncover
            #print("Choosing Safe Tile")
            #self.__board[safe[0][0]][safe[0][1]] = 0
            self.__currX = safe[0][0]
            self.__currY = safe[0][1]
            return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1])
        else:
            # no known safe tiles exist
            print("no safe tiles left!", len(safe), safe)
            idk = self.get_uncertain() # get unknown tile to process
            if len(idk) != 0: # if there exists at least one unknown tile
                print("taking random tile")
                #print("Choosing Uncertain Tile")
                rand = random.choice(idk) # randomly choose a tile to uncover
                self.__currX = rand[0]
                self.__currY = rand[1]
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

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################


    def get_neighbors(self, x, y):
        neighbors = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                     (x, y - 1), (x, y + 1),
                     (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]
        return list(filter(lambda n: (n[0] >= 0 and n[0] < self.__rows) and (n[1] >= 0 and n[1] < self.__cols), neighbors))
    
    
    def get_safe(self):
        safe = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j].safe and self.__board[i][j].covered:
                    safe.append((i, j))
        return safe
    
    def get_uncertain(self):
        idk = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j].covered:
                    idk.append((i, j))
        return idk

    def get_uncovered_neighbors(self, x, y): return list(filter(lambda tile: not self.__board[tile[0]][tile[1]].covered and not self.__board[tile[0]][tile[1]].flag, self.get_neighbors(x,y)))

    def get_covered_neighbors(self, x, y): return list(filter(lambda tile: self.__board[tile[0]][tile[1]].covered, self.get_neighbors(x,y)))

    def get_flagged_neighbors(self, x, y): return list(filter(lambda tile: self.__board[tile[0]][tile[1]].flag, self.get_neighbors(x,y)))
    
    # updates the elabels in a tile's neighborhood
    def update_elabels(self, x, y):
        # update tile's elabel
        tile = self.__board[x][y]
        tile.elabel = tile.label - len(self.get_flagged_neighbors(x, y))
        # update tile's neighbors' elabels
        for n in self.get_uncovered_neighbors(x, y):
            tile = self.__board[n[0]][n[1]]
            tile.elabel = tile.label - len(self.get_flagged_neighbors(x, y))
        return

    def model_check(self):
        # get U/C in frontier
        uncovered = self.__frontier.copy()
        covered = []
        for f in uncovered:
            covered.append(self.get_covered_neighbors(f[0],f[1]))

        for c in covered:
            # TODO: generate assignments to C
            # TODO: given assignment to C, check if elabel of each tile in U is satisfied
            pass
        return
