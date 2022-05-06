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
        if number != -1:
            self.__board[self.__currX][self.__currY] = number
        # check if we're done
        if self.__numCovered == self.__totalMines:
            return Action(AI.Action.LEAVE)
        # figure out UNCOVER(X,Y)
        neighbors = self.getNeighbors(self.__currX, self.__currY)
        # todo: try simple rule of thumb
        # uncover all neighbors if 0
        if number == 0:
            for n in neighbors:
                # uncover if covered
                if self.__board[n[0], n[1]] == -1:
                    return Action(Action.UNCOVER, n[0], n[1])

        if number == 1:
            uncovered = list(filter(lambda ne: (self.__board[ne[0]][ne[1]] == -1), neighbors))
			rand_uncover = random.choice(uncovered)
			return Action(Action.UNCOVER, rand_uncover[0], rand_uncover[1])
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
        for n in neighbors:
            # check if in bounds
            if n[0] < 0 or n[0] >= self.__rows:
                neighbors.remove(n)
            if n[1] < 0 or n[1] >= self.__cols:
                neighbors.remove(n)
            # check if covered
        return neighbors
