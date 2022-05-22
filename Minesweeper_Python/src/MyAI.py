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
        # int label, -1 = covered, 0-8 = label
        self.__board = [[-1 for x in range(colDimension)] for y in range(rowDimension)]

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

    def getAction(self, number: int) -> "Action Object":

        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        # update board
        print("percept number:", number, "current x/y:", self.__currX, self.__currY)

        if number >= 0:  # a/n un/flagging was not done, so we may set the label of the tile at the board
            # do not decrement numCovered here; causes the game to quit early in some cases
            tile = self.__board[self.__currX][self.__currY]  # get the current tile from the board
            tile.label = number  # self.__board[self.__currX][self.__currY] = number; set the tile's label
            tile.covered = False  # mark tile as uncovered on the board

        if (self.__currX,
            self.__currY) not in self.__frontier and number != -1:  # add current tile to frontier if not already in frontier
            print("Adding to frontier")
            self.__frontier.append((self.__currX, self.__currY))

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
                self.__board[flagged[0][0]][
                    flagged[0][1]].flag = True  # set flag status to true (has been/will be flagged on board)
                self.__board[flagged[0][0]][flagged[0][1]].safe = False
                return Action(AI.Action.FLAG, flagged[0][0], flagged[0][1])
            else:
                # check if there are any safe tiles (-3)
                safe = self.get_safe()  # get a safe tile to process
                if len(safe) != 0:  # if there exists at least one safe tile, uncover
                    print("Choosing a safe tile")
                    # pick one of the safe tiles to uncover
                    self.__currX = safe[0][0]
                    self.__currY = safe[0][1]
                    self.__numCovered -= 1  # a tile was uncovered, decrement covered count
                    return Action(AI.Action.UNCOVER, safe[0][0], safe[0][1])
                else:
					idk = self.get_uncertain()  # get unknown tile to process
					if len(idk) != 0:  # if there exists at least one unknown tile
						print("Choosing Uncertain Tile")
						rand = random.choice(idk)  # randomly choose a tile to uncover
						self.__currX = rand[0]
						self.__currY = rand[1]
						self.__numCovered -= 1  # a tile was uncovered, decrement covered count
						return Action(AI.Action.UNCOVER, rand[0], rand[1])

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

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
        return list(filter(
            lambda tile: not self.__board[tile[0]][tile[1]].covered and not self.__board[tile[0]][tile[1]].flag and not
            self.__board[tile[0]][tile[1]].mine, self.get_neighbors(x, y)))  #

    def get_uncertain_neighbors(self, x, y):
        """Gets all neighboring covered (but not mine/flagged) tiles"""
        # covered, not flag or mine
        return list(filter(
            lambda tile: self.__board[tile[0]][tile[1]].covered and not self.__board[tile[0]][tile[1]].mine and not
            self.__board[tile[0]][tile[1]].flag, self.get_neighbors(x, y)))

    def get_uncovered_neighbors(self, x, y):
        """Gets all neighboring uncovered (but not mine/flagged) tiles"""
        # covered, not flag or mine
        return list(filter(lambda tile: not self.__board[tile[0]][tile[1]].covered, self.get_neighbors(x, y)))

    def get_flagged_neighbors(self, x, y):
        """Gets all neighboring flagged/mine tiles"""
        # mine or flag
        return list(filter(lambda tile: self.__board[tile[0]][tile[1]].mine or self.__board[tile[0]][tile[1]].flag,
                           self.get_neighbors(x,
                                              y)))  # and self.__board[tile[0]][tile[1]].covered, self.getNeighbors(x,y)))

    def update_elabels(self):
        """Update effective labels of tiles in frontier"""
        for f in self.__frontier:
            tile = self.__board[f[0]][f[1]]
            tile.elabel = tile.label - len(self.get_flagged_neighbors(f[0], f[1]))

    def update_frontier(self):
        for f in self.__frontier:
            tile = self.__board[f[0]][f[1]]
            if tile.flag or tile.mine:
                self.__frontier.remove(f)
                continue
            uncertain = self.get_uncertain_neighbors(f[0], f[1])
            if len(uncertain) == 0:
                self.__frontier.remove(f)
                continue
            if tile.elabel == 0:
                print("All safe", f)
                for n in uncertain:
                    self.__board[n[0]][n[1]].safe = True
                # all neighbors either flagged or uncovered = tile no longer in frontier
                self.__frontier.remove(f)
            elif tile.elabel == len(uncertain):
                print("All mines", f)
                for n in uncertain:
                    self.__board[n[0]][n[1]].mine = True
                # all neighbors either flagged or uncovered = tile no longer in frontier
                self.__frontier.remove(f)
