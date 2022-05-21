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

    class __Tile(): # add tile class to describe board state
        def __init__(self) -> None:
            self.covered = True
            self.mine = False # has been determined to be a mine
            self.flag = False # has been marked on board
            self.safe = False
            self.label = -1
            self.elabel = -1
        
        def __str__(self): # f strings only exist in python 3.6; incompatible
            return # f"L:{self.label}/EL:{self.elabel}/S:{self.safe}/F:{self.flag}"




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
        
        # create a frontier to contain the tiles currently operating on (tiles we aren't done with?)
        self.__frontier = [(startX, startY)]

        # create a board of tiles; each will contain tile state information
        self.__board = [[self.__Tile() for c in range(colDimension)] for r in range(rowDimension)]
        
        # -1 means covered
        # -2 means flagged
        # -3 means safe
        # -4 means flagged in game
        #self.__board = [[-1 for c in range(colDimension)] for r in range(rowDimension)]

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

    def getAction(self, number: int) -> "Action Object":
        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        # update board
        print("percept number:", number, "current x/y:", self.__currX, self.__currY)
        if number >= 0: # a/n un/flagging was not done, so we may set the label of the tile at the board
            print("Updating")
            self.__numCovered -= 1 # a tile was uncovered
            tile = self.__board[self.__currX][self.__currY] # get the current tile
            tile.label = number   # self.__board[self.__currX][self.__currY] = number; set the tile's label
            tile.covered = False  # uncover the tile on the board
        
        if (self.__currX, self.__currY) not in self.__frontier: # add to frontier if not already in frontier
            print("Adding to frontier")
            self.__frontier.append((self.__currX, self.__currY))

        # check if we're done
        # if number of mines is M, and M mines have been identified (on board), 
        # all other covered tiles are safe. (may need to be implemented if this skip causes issues)
        if self.__numCovered == self.__totalMines:
            print("Leaving")
            return Action(AI.Action.LEAVE)
        # figure out UNCOVER(X,Y)
        neighbors = self.getNeighbors(self.__currX, self.__currY)
        
        # logic rules
        # 1. if tile = number N and has N flagged (-2) neighbors, all uncertain (-1) neighbors are safe; 
        # change to "safe" on board (-3)
        # 2. if tile = number N and has N uncertain (-1) neighbors, all those neighbors are mines (-2)
        uncertain = list(filter(lambda ne: (self.__board[ne[0]][ne[1]].covered and not self.__board[ne[0]][ne[1]].flag and not self.__board[ne[0]][ne[1]].mine), neighbors))
        flagged = list(filter(lambda ne: (self.__board[ne[0]][ne[1]].mine), neighbors))

        if (number == len(flagged)): # the number of flagged is equal to the tile number
            print("All safe")
            for x, y in uncertain:
                # mark all other unknown tiles as safe
                self.__board[x][y].safe = True
            # all neighbors either flagged or uncovered = tile no longer in frontier
            self.__frontier.remove((self.__currX, self.__currY)) 
        elif (number == len(uncertain)): # the number of unknowns is equal to tile number
            print("All mines")
            for x, y in uncertain:
                # mark all unknown tiles as mines
                self.__board[x][y].mine = True
            # all neighbors either flagged or uncovered = tile no longer in frontier
            self.__frontier.remove((self.__currX, self.__currY)) 

        # update effective labels
        print("Updating elabels")
        self.update_elabels(self.__currX, self.__currY)
        # get frontier, uncovered unflagged neighbors are safe if elabels are zero
        for f in self.__frontier:
            tile = self.__board[f[0]][f[1]]
            if tile.elabel == 0:
                neighborhood = self.get_uncovered_neighbors(f[0], f[1])
                for n in neighborhood:
                    self.__board[n[0]][n[1]].safe = True

        # actions
        flagged = self.getFlagged()
        if len(flagged) != 0:
            print("Updating flags")
            # check for tiles that are found to have mines; flag on board
            self.__board[flagged[0][0]][flagged[0][1]].flag = True # set flag status to true
            return Action(AI.Action.FLAG, flagged[0][0], flagged[0][1])
        else:
            # check if there are any safe tiles (-3)
            # pick one of the safe tiles to do
            safe = self.getSafe() # get a safe tile to process
            if len(safe) != 0: # if there exists at least one safe tile, uncover
                #print("Choosing Safe Tile")
                #self.__board[safe[0][0]][safe[0][1]] = 0
                print("Choosing a safe tile")
                self.__currX = safe[0][0]
                self.__currY = safe[0][1]
                return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1])
            else:
                # re evaluate to find safe tiles
                print("Reevaluating")
                for i in range(self.__rows):
                    for j in range(self.__cols):
                        if not self.__board[i][j].covered:
                            neighbors = self.getNeighbors(i, j)
                            uncertain = list(filter(lambda ne: (self.__board[ne[0]][ne[1]].covered and not self.__board[ne[0]][ne[1]].flag), neighbors))
                            flagged = list(filter(lambda ne: (self.__board[ne[0]][ne[1]].flag or self.__board[i][j].mine), neighbors))
                            if (self.__board[i][j].label == len(flagged)):
                                for x, y in uncertain:
                                    self.__board[x][y].safe = True
                            elif (self.__board[i][j].label == len(uncertain)):
                                for x, y in uncertain:
                                    self.__board[x][y].mine = True
                # get any newly generated safe tiles, if possible
                safe = self.getSafe() # get a safe tile to process
                if len(safe) != 0: # if there exists at least one safe tile, uncover
                    print("Choosing a safe tile")
                    self.__currX = safe[0][0]
                    self.__currY = safe[0][1]
                    return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1]) 
                else: # the first uncertian choice
                    # no known safe tiles exist
                    idk = self.getUncertain() # get unknown tile to process
                    if len(idk) != 0: # if there exists at least one unknown tile
                        print("Choosing Uncertain Tile")
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
        """Gets the nearest (valid) neighbors of the tile at x,y on the game board"""
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
        """Gets all known safe tiles on the game board"""
        # safe, uncovered tiles
        safe = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j].safe and self.__board[i][j].covered:
                    safe.append((i, j))
        return safe
    
    def getUncertain(self):
        """Gets all (status) unknown tiles on the game board"""
        # unknown tiles, unflagged (status unknown)
        idk = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j].covered and not self.__board[i][j].flag and not self.__board[i][j].mine:
                    idk.append((i, j))
        return idk

    def getFlagged(self):
        """Gets all known flagged tiles on the game board"""
        # unknown, flagged tiles
        flags = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j].flag:
                    flags.append((i, j))
        return flags

    def get_uncovered_neighbors(self, x, y): 
        return list(filter(lambda tile: not self.__board[tile[0]][tile[1]].covered and not self.__board[tile[0]][tile[1]].flag and not self.__board[tile[0]][tile[1]].mine, self.getNeighbors(x,y)))

    def get_covered_neighbors(self, x, y): 
        return list(filter(lambda tile: self.__board[tile[0]][tile[1]].covered and not self.__board[tile[0]][tile[1]].flag and not self.__board[tile[0]][tile[1]].mine, self.getNeighbors(x,y)))

    def get_flagged_neighbors(self, x, y): 
        return list(filter(lambda tile: self.__board[tile[0]][tile[1]].flag and self.__board[tile[0]][tile[1]].mine and self.__board[tile[0]][tile[1]].covered, self.getNeighbors(x,y)))

    def update_elabels(self, x, y):
        """Update a tile's effective label"""
        # update tile's elabel
        tile = self.__board[x][y]
        # the effective label is the number of remaining mines in the tile's neighborhood
        tile.elabel = tile.label - len(self.get_flagged_neighbors(x, y))
        #update tile's neighbors' elabels
        for n in self.get_uncovered_neighbors(x, y):
            tile = self.__board[n[0]][n[1]]
            tile.elabel = tile.label - len(self.get_flagged_neighbors(x, y))
        for i in range(self.__rows):
            for j in range(self.__cols):
                print(self.__board[i][j].elabel, end=" ")
            print()
        # return

    def model_check(self): 
        """I'm leavin this to you since idk what ur goal is"""
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
