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
import heapq

class PriorityQueue:
    def __init__(self):
        self.pq = []

    def push(self, item):
        heapq.heappush(self.pq, item)

    def pop(self):
        return heapq.heappop(self.pq)
    
    def remove(self, item):
        for i in self.pq:
            if i == item:
                self.pq.remove(item)

    def isEmpty(self):
        return len(self.pq) == 0

    def isIn(self, item):
        for i in self.pq:
            if i == item:
               return True
        return False


class MyAI(AI):

    class __Tile(): 
        # add tile class to describe board state
        def __init__(self, x, y) -> None:
            # -1  means covered (unknown)
            # -2  means flagged
            # -3  means safe
            # -4  means flagged in game
            # 0-8 is tile number (uncovered)
            self.status = -1
            self.label = -1
            self.elabel = -1
            self.x = x
            self.y = y
        
        def __str__(self): # f strings only exist in python 3.6; incompatible
            return # f"L:{self.label}/EL:{self.elabel}/S:{self.safe}/F:{self.flag}"

        def __cmp__(self, other): # f strings only exist in python 3.6; incompatible
            return (self.label > other.label) - (self.label < other.label) # cmp(self.label, other.label)

        def __lt__(self, other): # f strings only exist in python 3.6; incompatible
            return self.label < other.label

        def __eq__(self, other): # f strings only exist in python 3.6; incompatible
            return self.label == other.label # cmp(self.label, other.label)

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        self.__rows = rowDimension
        self.__cols = colDimension
        self.__totalMines = totalMines
        self.__currX = startX
        self.__currY = startY
        self.__numCovered = (self.__rows * self.__cols) - self.__totalMines
        # int label, negative = covered, 0-8 = label (uncovered)

        # create a board of tiles; each will contain tile state information
        self.__board = [[self.__Tile(r, c) for c in range(colDimension)] for r in range(rowDimension)]

        # create a frontier to contain the tiles currently operating on (tiles we aren't done with?)
        self.__frontier = PriorityQueue()
        self.put_in_frontier(self.__board[self.__currX][self.__currY])
        
        
        # self.__board = [[-1 for c in range(colDimension)] for r in range(rowDimension)]

    ##################################################################################################################
    # Methods
    ##################################################################################################################

    def getAction(self, number: int) -> "Action Object":
        
        # update board
        print("percept number:", number, "current x/y:", self.__currX, self.__currY)
        tile = self.__board[self.__currX][self.__currY] # get the current tile from the board
        if number >= 0: # a/n un/flagging was not done (uncovered), set the label of the tile at the board
            print("Updating")
            # do not decrement numCovered here; causes the game to quit early in some cases
            tile.label = number   # self.__board[self.__currX][self.__currY] = number; set the tile's label
            self.update_elabel(self.__currX, self.__currY)  # hrm
            tile.status = number  # mark tile as uncovered on the board
        
        self.put_in_frontier(tile)

        # check if we're done
        # if number of mines is M, and M mines have been identified (on board), 
        # all other covered tiles are safe. (may need to be implemented if this skip causes issues)
        if self.__numCovered == self.__totalMines:
            print("Leaving")
            return Action(AI.Action.LEAVE)  
        
        # logic rules
        # 1. if tile = number N and has N flagged (-2) neighbors, all uncertain (-1) neighbors are safe; 
        # change to "safe" on board (-3)
        # 2. if tile = number N and has N uncertain (-1) neighbors, all those neighbors are mines (-2)
        
        uncertain = self.get_uncertain_neighbors(self.__currX, self.__currY)
        flagged = self.get_flagged_neighbors(self.__currX, self.__currY)

        if (number == len(flagged)): # the number of flagged is equal to the tile number (found all mines in neighborhood)
            print("All safe")
            for x, y in uncertain:
                # mark all other unknown tiles as safe
                self.__board[x][y].status = -3
            # all neighbors either flagged or uncovered = tile no longer has unknowns = tile not in frontier
            print("removing from frontier1")
            self.remove_from_frontier(tile)
            print("removed1")
        
        elif (number == len(uncertain)): # the number of unknowns is equal to tile number
            print("All mines")
            for x, y in uncertain:
                # mark all unknown tiles as mines
                self.__board[x][y].status = -2
                # found mine, update elabel
                self.update_mine_elabel(x, y)
            # all neighbors either flagged or uncovered = tile no longer in frontier
            print("f2")
            self.remove_from_frontier(tile)
            print("f2")

        # iterate frontier; covered unflagged neighbors are safe if elabels are zero
        print("f2")
        for f in self.__frontier.pq:
            if f.elabel == 0:
                print("f3-2")
                neighborhood = self.get_uncertain_neighbors(f.x, f.y)
                for n in neighborhood:
                    self.__board[n[0]][n[1]].status = -3
                    print("f3-3")

        # actions
        # check and update known mines that havent been flagged on board
        flagged = self.get_flagged()
        if len(flagged) != 0:
            print("Updating flags")
            # check for tiles that are found to have mines; flag on board
            print(flagged[0][0],flagged[0][1], len(flagged))
            self.__board[flagged[0][0]][flagged[0][1]].status = -4 # set flag status to true (has been/will be flagged on board)
            print("Flagging")
            return Action(AI.Action.FLAG, flagged[0][0], flagged[0][1])
        else:
            # check if there are any safe tiles (-3)
            safe = self.get_safe() # get a safe tile to process
            if len(safe) != 0: # if there exists at least one safe tile, uncover
                print("Choosing a safe tile1")
                # pick one of the safe tiles to uncover
                self.__currX = safe[0][0]
                self.__currY = safe[0][1]
                print("set x and y")
                print(safe[0][0],safe[0][1], len(safe))
                # self.__board[safe[0][0]][safe[0][1]].covered = False
                print("decr num covered")
                self.__numCovered -= 1 # a tile was uncovered, decrement covered count
                print("Returning action")
                return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1])
            else:
                # re evaluate to find new safe tiles
                print("Reevaluating")
                for i in range(self.__rows):
                    for j in range(self.__cols):
                        if self.__board[i][j].status >= 0:

                            uncertain = self.get_uncertain_neighbors(i, j)
                            flagged = self.get_flagged_neighbors(i, j) 
                            print("got some neighbors")

                            if (self.__board[i][j].label == len(flagged)): # all mines in the area have been found
                                print("flagged")
                                for x, y in uncertain:
                                    print("uncertain")
                                    self.__board[x][y].status = -3
                                print("removing")
                                self.remove_from_frontier(self.__board[i][j])
                                print("removed")

                            elif (self.__board[i][j].label == len(uncertain)): # all uncertain tiles in the area are mines
                                print("uncertain")
                                for x, y in uncertain:
                                    self.__board[x][y].status = -2
                                    # found mine, update elabel
                                    self.update_mine_elabel(x, y)
                                print("f4")
                                self.remove_from_frontier(self.__board[i][j])
                                print("f4")
                        for f in self.__frontier.pq:
                            if f.elabel == 0:
                                neighborhood = self.get_uncertain_neighbors(f.x, f.y)
                                for n in neighborhood:
                                    self.__board[n[0]][n[1]].status = -3

                print("checking again")
                # get any newly generated safe tiles, if possible
                safe = self.get_safe() # get a safe tile to process
                if len(safe) != 0: # if there exists at least one safe tile, uncover
                    print("Choosing a safe tile2")
                    self.__currX = safe[0][0]
                    self.__currY = safe[0][1]
                    print(safe[0][0],safe[0][1], len(safe))
                    # self.__board[safe[0][0]][safe[0][1]].covered = False
                    self.__numCovered -= 1 # a tile was uncovered, decrement covered count
                    return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1]) 
                else: # the first uncertian choice, causes the most issues because it's randomly chosen
                    # no known safe tiles exist
                    print("Iterate thru frontier")
                    # iterate through the frontier to find a move first. 
                    if self.__frontier.isEmpty(): #len(self.__frontier.p) != 0:
                        for tile in self.__frontier.pq:
                            uncertain = self.get_uncertain_neighbors(f[0], f[1])
                            flagged = self.get_flagged_neighbors(f[0], f[1]) 
                            if (self.__board[f[0]][f[1]].label == len(flagged)): # all mines have been flagged
                                for x, y in uncertain:
                                    self.__board[x][y].status = -3
                                self.remove_from_frontier(self.__board[f[0]][f[1]])
                            elif (self.__board[f[0]][f[1]].label == len(uncertain)): # all uncertain tiles in the area are mines
                                for x, y in uncertain:
                                    self.__board[x][y].status = -2
                                    # found mine, update elabel
                                    self.update_mine_elabel(x, y)
                                self.remove_from_frontier(self.__board[f[0]][f[1]])

                        for f in self.__frontier.pq:
                            if f.elabel == 0:
                                neighborhood = self.get_uncertain_neighbors(f.x, f.y)
                                for n in neighborhood:
                                    self.__board[n[0]][n[1]].status = -3

                    # get any newly generated safe tiles, if possible
                    safe = self.get_safe() # get a safe tile to process
                    if len(safe) != 0: # if there exists at least one safe tile, uncover
                        print("Choosing a safe tile3")
                        self.__currX = safe[0][0]
                        self.__currY = safe[0][1]
                        print(safe[0][0],safe[0][1], len(safe))
                        # self.__board[safe[0][0]][safe[0][1]].covered = False
                        self.__numCovered -= 1 # a tile was uncovered, decrement covered count
                        return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1]) 
                    else: # the first uncertian choice, causes the most issues because it's randomly chosen
                        # no known safe tiles exist
                        idk = self.get_uncertain() # get unknown tile to process
                        if len(idk) != 0: # if there exists at least one unknown tile
                            print("Choosing Uncertain Tile")
                            rand = random.choice(idk) # randomly choose a tile to uncover
                            self.__currX = rand[0]
                            self.__currY = rand[1]
                            print(rand[0], rand[1], len(idk))
                            self.__numCovered -= 1 # a tile was uncovered, decrement covered count
                            print("decr num covered")
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
                if self.__board[i][j].status == -3:
                    safe.append((i, j))
        return safe
    
    def get_uncertain(self):
        """Gets all (status) unknown tiles on the game board"""
        # unknown tiles, unflagged (status unknown)
        idk = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__board[i][j].status == -1:
                    idk.append((i, j))
        return idk

    def get_flagged(self):
        """Gets all known mine tiles on the game board"""
        # unknown, flagged tiles
        flags = []
        for i in range(self.__rows):
            for j in range(self.__cols):
                # get mine tiles that are not marked on the board
                if self.__board[i][j].status == -2:
                    flags.append((i, j))
        return flags

    def get_uncovered_neighbors(self, x, y): 
        """Gets all neighboring uncovered tiles"""
        return list(filter(lambda tile: self.__board[tile[0]][tile[1]].status >= 0, self.get_neighbors(x,y))) # and not self.__board[tile[0]][tile[1]].flag and not self.__board[tile[0]][tile[1]].mine

    def get_uncertain_neighbors(self, x, y):
        """Gets all neighboring covered (but not mine/flagged) tiles"""
        # covered, not flag or mine
        return list(filter(lambda tile: self.__board[tile[0]][tile[1]].status == -1, self.get_neighbors(x,y)))

    def get_flagged_neighbors(self, x, y): 
        """Gets all neighboring flagged/mine tiles"""
        # mine or flag
        return list(filter(lambda tile: self.__board[tile[0]][tile[1]].status == -2 or self.__board[tile[0]][tile[1]].status == -4, self.get_neighbors(x,y))) # and self.__board[tile[0]][tile[1]].covered, self.getNeighbors(x,y)))

    def update_elabel(self, x, y):
        """Update a tile's effective label"""
        # update tile's elabel
        tile = self.__board[x][y]
        # the effective label is the number of remaining mines in the tile's neighborhood
        tile.elabel = tile.label - len(self.get_flagged_neighbors(x, y))

    def update_mine_elabel(self, x, y):
        """Update the effective label of the neighbors of a mine tile"""
        for n in self.get_uncovered_neighbors(x, y):
            tile = self.__board[n[0]][n[1]]
            self.update_elabel(n[0], n[1])

    def model_check(self): 
        """I'm leavin this to you since idk what ur goal is"""
        # get U/C in frontier
        uncovered = self.__frontier.copy()
        covered = []
        for f in uncovered:
            covered.append(self.get_uncertain_neighbors(f[0],f[1]))

        for c in covered:
            # TODO: generate assignments to C
            # TODO: given assignment to C, check if elabel of each tile in U is satisfied
            pass
        return
    
    def put_in_frontier(self, tile):
        if not self.__frontier.isIn(tile):
            self.__frontier.push(tile)

    def remove_from_frontier(self, tile):
        if self.__frontier.isIn(tile):
            self.__frontier.remove(tile)

