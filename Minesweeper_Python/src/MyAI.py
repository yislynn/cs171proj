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
from turtle import update

from AI import AI
from Action import Action


class MyAI(AI):

    class __Tile(): 
        # add tile class to describe board state
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
        # self.__board = [[-1 for c in range(colDimension)] for r in range(rowDimension)]

    ##################################################################################################################
    # Methods
    ##################################################################################################################

    def getAction(self, number: int) -> "Action Object":
        # update board
        print("percept number:", number, "current x/y:", self.__currX, self.__currY)
        
        if number >= 0: # a/n un/flagging was not done, so we may set the label of the tile at the board
            # do not decrement numCovered here; causes the game to quit early in some cases
            tile = self.__board[self.__currX][self.__currY] # get the current tile from the board
            tile.label = number   # self.__board[self.__currX][self.__currY] = number; set the tile's label
            tile.covered = False  # mark tile as uncovered on the board
        
        if (self.__currX, self.__currY) not in self.__frontier and number != -1: # add current tile to frontier if not already in frontier
            print("Adding to frontier")
            self.__frontier.append((self.__currX, self.__currY))

        # check if we're done
        # if number of mines is M, and M mines have been identified (on board), 
        # all other covered tiles are safe. (may need to be implemented if this skip causes issues)
        if self.__numCovered == self.__totalMines:
            print("Leaving")
            return Action(AI.Action.LEAVE)

        # update effective labels
        print("Updating elabels")
        self.update_elabels()
        # get frontier, covered unflagged neighbors are safe if elabels are zero
        self.update_frontier()

        # actions
        flagged = self.get_flagged()
        if len(flagged) != 0:
            print("Updating flags", flagged)
            # check for tiles that are found to have mines; flag on board
            self.__board[flagged[0][0]][flagged[0][1]].flag = True # set flag status to true (has been/will be flagged on board)
            self.__board[flagged[0][0]][flagged[0][1]].safe = False
            return Action(AI.Action.FLAG, flagged[0][0], flagged[0][1])
        else:
            # check if there are any safe tiles (-3)
            safe = self.get_safe() # get a safe tile to process
            if len(safe) != 0: # if there exists at least one safe tile, uncover
                print("Choosing a safe tile")
                # pick one of the safe tiles to uncover
                self.__currX = safe[0][0]
                self.__currY = safe[0][1]
                self.__numCovered -= 1 # a tile was uncovered, decrement covered count
                return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1])
            else:
                # re evaluate to find new safe tiles
                print("Reevaluating")
                for i in range(self.__rows):
                    for j in range(self.__cols):
                        if not self.__board[i][j].covered:
                            # neighbors = self.get_neighbors(i, j)
                            # list(filter(lambda ne: (self.__board[ne[0]][ne[1]].covered and not self.__board[ne[0]][ne[1]].flag), neighbors))
                            uncertain = self.get_uncertain_neighbors(i, j)
                            if len(uncertain) == 0: continue
                            # list(filter(lambda ne: (self.__board[ne[0]][ne[1]].flag or self.__board[i][j].mine), neighbors))
                            flagged = self.get_flagged_neighbors(i, j) 
                            if (self.__board[i][j].label == len(flagged)): # all mines have been flagged
                                for x, y in uncertain:
                                    self.__board[x][y].safe = True
                                self.__frontier.remove((i, j)) 
                            elif (self.__board[i][j].elabel == len(uncertain)): # all uncertain tiles in the area are mines
                                for x, y in uncertain:
                                    self.__board[x][y].mine = True
                                self.__frontier.remove((i, j)) 
                # get any newly generated safe tiles, if possible
                safe = self.get_safe() # get a safe tile to process
                flagged = self.get_flagged()
                if len(safe) != 0: # if there exists at least one safe tile, uncover
                    print("Choosing a safe tile")
                    self.__currX = safe[0][0]
                    self.__currY = safe[0][1]
                    self.__numCovered -= 1 # a tile was uncovered, decrement covered count
                    return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1]) 
                elif len(flagged) != 0:
                    self.__board[flagged[0][0]][flagged[0][1]].safe = False
                    self.__board[flagged[0][0]][flagged[0][1]].flag = True
                    return Action(AI.Action.FLAG, flagged[0][0], flagged[0][1])
                else: # the first uncertian choice, causes the most issues because it's randomly chosen
                    # no known safe tiles exist
                    idk = self.get_uncertain() # get unknown tile to process
                    if len(idk) != 0: # if there exists at least one unknown tile
                        print("Choosing Uncertain Tile")
                        rand = random.choice(idk) # randomly choose a tile to uncover
                        self.__currX = rand[0]
                        self.__currY = rand[1]
                        self.__numCovered -= 1 # a tile was uncovered, decrement covered count
                        return Action(AI.Action.UNCOVER, rand[0], rand[1])
                    else: # there are no unknown tiles = all tiles are uncovered = game is won = leave
                        return Action(AI.Action.LEAVE)
    
    ##################################################################################################################
    # Methods
    ##################################################################################################################
    
    def get_neighbors(self, x, y):
        """Gets the nearest (valid) neighbors of the tile at x,y on the game board"""
        neighbors = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                     (x, y - 1), (x, y + 1),
                     (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]
        ne = []
        for n in neighbors:
            # check if in bounds
            if n[1] < self.__cols and n[1] >= 0 and n[0] < self.__rows and n[0] >= 0:
                ne.append(n)
        return ne

    def get_safe(self):
        """Gets all known safe tiles on the game board"""
        # safe, uncovered tiles
        safe = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j].safe and self.__board[i][j].covered:
                    safe.append((i, j))
        return safe
    
    def get_uncertain(self):
        """Gets all (status) unknown tiles on the game board"""
        # unknown tiles, unflagged (status unknown)
        idk = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j].covered and not self.__board[i][j].flag and not self.__board[i][j].mine:
                    idk.append((i, j))
        return idk

    def get_flagged(self):
        """Gets all known mine tiles on the game board"""
        # unknown, flagged tiles
        flags = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                # get mine tiles that are not marked on the board
                if self.__board[i][j].mine and not self.__board[i][j].flag:
                    flags.append((i, j))
        return flags

    def get_uncovered_neighbors(self, x, y): 
         """Gets all neighboring uncovered tiles"""
         return list(filter(lambda tile: not self.__board[tile[0]][tile[1]].covered, self.get_neighbors(x,y))) # and not self.__board[tile[0]][tile[1]].flag and not self.__board[tile[0]][tile[1]].mine

    def get_uncertain_neighbors(self, x, y):
        """Gets all neighboring covered (but not mine/flagged) tiles"""
        # covered, not flag or mine
        return list(filter(lambda tile: self.__board[tile[0]][tile[1]].covered and not self.__board[tile[0]][tile[1]].mine and not self.__board[tile[0]][tile[1]].flag, self.get_neighbors(x,y)))

    def get_flagged_neighbors(self, x, y): 
        """Gets all neighboring flagged/mine tiles"""
        # mine or flag
        return list(filter(lambda tile: self.__board[tile[0]][tile[1]].mine or self.__board[tile[0]][tile[1]].flag, self.get_neighbors(x,y))) # and self.__board[tile[0]][tile[1]].covered, self.getNeighbors(x,y)))

    def update_elabels(self):
        """Update effective labels of tiles in frontier"""
        for f in self.__frontier:
            tile = self.__board[f[0]][f[1]]
            tile.elabel = tile.label - len(self.get_flagged_neighbors(f[0], f[1]))

    def update_frontier(self):
        for f in self.__frontier:
            tile = self.__board[f[0]][f[1]]
            # remove any flagged/surrounded tiles - shouldn't be needed but better safe than sorry
            if tile.flag or tile.mine:
                self.__frontier.remove(f)
                continue
            uncertain = self.get_uncertain_neighbors(f[0], f[1])
            if len(uncertain) == 0:
                self.__frontier.remove(f)
                continue
            # find safe/mine tiles
            if tile.elabel == 0:
                print("All safe", f)                
                for n in uncertain:
                    self.__board[n[0]][n[1]].safe = True
                # all neighbors either flagged or uncovered = tile no longer in frontier
                self.__frontier.remove((f))
            elif tile.elabel == len(uncertain):
                print("All mines", f)
                for n in uncertain:
                    self.__board[n[0]][n[1]].mine = True
                # all neighbors either flagged or uncovered = tile no longer in frontier
                self.__frontier.remove((f))
