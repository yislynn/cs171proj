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
# ==============================CS-199==================================
import random

from AI import AI
from Action import Action


class Sentence():
    """
    Logical statement 
    1. set of board tiles,
    2. count of the number of those cells which are mines.
    """

    def __init__(self, tiles, count):
        self.tiles = set(tiles)
        self.count = count

    def __eq__(self, other):
        if other == None:
            return False
        return self.tiles == other.tiles and self.count == other.count

    def __str__(self):
        return "{} = {}".format(self.tiles, self.count)

    def known_mines(self):
        if len(self.tiles) == self.count:
            return self.tiles
        # else:
        #     return 

    def known_safes(self):
        if self.count == 0:
            return self.tiles

    def mark_mine(self, tile):
        if tile in self.tiles:
            self.tiles.remove(tile)
            self.count -= 1

    def mark_safe(self, tile):
        if tile in self.tiles:
            self.tiles.remove(tile)

######################################################################################################################

class Tile(): 
    # add tile class to describe board state
    # can probably improve the status somehow
    # get rid of safe and flagged in game?
    def __init__(self, x, y, bx, by) -> None:
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

    def uncover(self, num) -> None:
        if num >= 0:
            self.label = num
            self.status = num
    
    def flag(self) -> None:
        if self.status < 0:
            self.status = -4
       
    def __str__(self): # f strings only exist in python 3.6; incompatible
        return "Label:{}/ELabel:{}/Status:{}".format(self.label, self.elabel, self.status)

    def __cmp__(self, other):
        return (self.label > other.label) - (self.label < other.label) # cmp(self.label, other.label)

    def __lt__(self, other):
        return self.label < other.label

    def __eq__(self, other):
        return self.label == other.label # cmp(self.label, other.label)
    
    def __hash__(self):
        return hash(repr(self)) # cmp(self.label, other.label)


class MyAI(AI):
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        self.__rows = rowDimension
        self.__cols = colDimension
        self.__totalMines = totalMines
        self.__currX = startX
        self.__currY = startY
        self.__numCovered = (self.__rows * self.__cols) - self.__totalMines
        # create a board of tiles; each will contain tile state information
        
        self.__board = [[Tile(r, c, rowDimension, colDimension) for c in range(colDimension)] for r in range(rowDimension)]

        ####
        self.__prev_move = Action(AI.Action.UNCOVER, startX, startY)
        
        # Keep track of which cells have been uncovered
        self.moves_made = set()
        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        self.knowledge_base = [] # list of all known facts about the game; knowledge, statement_list

        
        # self.solved = []
        self.moves = [] # solvable sentences
        self.frontier = []

    ##################################################################################################################
    # Methods
    ##################################################################################################################

    def getAction(self, number: int) -> "Action Object":
        x = self.__prev_move.getX()
        y = self.__prev_move.getY()

        print("action")
        if number >= 0:
            print("updated")
            self.__board[x][y].uncover(number)
            self.add_knowledge(self.__board[x][y], number)

            if (not self.__board[x][y] in self.solved) and (not self.__board[x][y] in self.frontier):
                print("add to frontier")
                self.frontier.append(self.__board[x][y])

        else:
            print("flag")
            self.__board[x][y].flag()

        return self.make_safe_move()

    
    ##################################################################################################################
    # Methods
    ##################################################################################################################

    def get_neighbors(self, x, y):
        """Gets the nearest (valid) neighbor coordinates of the tile at x,y on the game board"""
        neighbors = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                     (x, y - 1), (x, y + 1),
                     (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]
        ne = []
        for n in neighbors:
            # check if in bounds
            if n[1] < self.__cols and n[1] >= 0 and n[0] < self.__rows and n[0] >= 0:
                ne.append(n)
        return ne

    def get_tile_neighbors(self, tile):
        """Gets the neighboring tiles of the given tile"""
        n = self.get_neighbors(tile.x, tile.y)
        tiles = []
        for x,y in n:
            tiles.append(self.__board[x][y])
        return tiles
    
    def get_tile_safe(self, tile):
        """Gets the tiles that are considered safe"""
        n = self.get_neighbors(tile.x, tile.y)
        tiles = []
        for x,y in n:
            if self.__board[x][y].status == -3:
                tiles.append(self.__board[x][y])
        return tiles
    
    def get_tile_mines(self, tile):
        """Gets the neighbors that should have mines"""
        n = self.get_neighbors(tile.x, tile.y)
        tiles = []
        for x,y in n:
            if self.__board[x][y].status == -2 or self.__board[x][y].status == -4:
                tiles.append(self.__board[x][y])
        return tiles

    ##################################################################################################################
    def mark_mine(self, tile):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.append(tile)
        tile.status = -2
        for sentence in self.knowledge_base:
            sentence.mark_mine(tile)

    def mark_safe(self, tile):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.append(tile)
        tile.status = -3
        for sentence in self.knowledge_base:
            sentence.mark_safe(tile)

    def add_knowledge(self, tile, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        1.  mark the cell as a move that has been made
        2.  mark the cell as safe
        3.  add a new sentence to the AI's knowledge base
            based on the value of `cell` and `count`
        4.  mark any additional cells as safe or as mines
            if it can be concluded based on the AI's knowledge base
        5.  add any new sentences to the AI's knowledge base
            if they can be inferred from existing knowledge
        """
        self.moves_made.add(tile)
        self.safes.add(tile)
        self.mark_safe(tile)

        tiles = self.get_tile_neighbors(tile)
        self.knowledge_base.append(Sentence(tiles, count))

        self.solve_statements()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        print("find a move")
        self.find_move()
        
        if not self.moves:
            print("solving statements")
            self.solve_statements()

		# if can't make a inference, make a guess with possibility
        if not self.moves:
            print("make a giess")
            self.make_guess()

        next_move = self.moves.pop()
        print("get a move")
        self.last_move = next_move
        print("returning")
		#print("visit",next_move.getX(),next_move.getY(),next_move.getMove())
        return next_move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        raise NotImplementedError

######################################################################################################################
    def minus(self, left, right):
        if left.tiles.issubset(right.tiles):
            return Sentence(left.tiles, right.count - left.count)
        else:
            return None

    def isSolveable(self, stmt) -> bool:
        if len(stmt.tiles) == 0: # must be at least 1 element in list
            return False
        # there are no mines in the tile list or
        # all known tiles are mines
        if stmt.count == 0 or len(stmt.tiles) == stmt.count:
            return True
        return False

    def solve_statements(self):
        infer_list = []
        gen_new = True
        while gen_new:
            gen_new = False
            new_stmts = []
            for left in self.knowledge_base:
                for right in self.knowledge_base:
                    if left != right:
                        new_s = self.minus(left, right)
                        if new_s != None:	# gen a new & diff statement
                            if self.isSolveable(new_s):
                                if new_s not in infer_list:
                                    infer_list.append(new_s)
                            else:
                                if (new_s not in self.knowledge_base) and (new_s not in new_stmts):
                                    new_stmts.append(new_s)
                                    gen_new = True
            self.knowledge_base.extend(new_stmts)
        
        for s in infer_list:
            if s.count == 0:
                for tile in s.tiles:
                    self.mark_safe(tile)
                    self.moves.append(Action(AI.Action.UNCOVER,tile.x,tile.y))
            elif len(s.tiles)==s.count:
                for tile in s.tiles:
                    self.mark_mine(tile)
                    self.moves.append(Action(AI.Action.FLAG,tile.x,tile.y))

    def find_move(self) -> None:
        """Find a possible move by searching the frontier"""
        for tile in self.frontier:
            self.solve_block(tile)

    def make_guess(self) -> None:
        """Choose a random tile to uncover and append it to the moves list"""
        unsolved = [] # list of unknowns
        for x in range(0, self.__rows):
            for y in range(0, self.__cols):
                if (self.__board[x][y].status == -1):
                    unsolved.append((x,y))
        (x,y) = random.choice(unsolved)
        self.moves.append(Action(AI.Action.UNCOVER,x,y))

    def solve_block(self, b) -> None:
        # an issue?
        if b.status <= -1:
            return
        
        # check how many blocks around are solved or are mines.
        block = self.get_tile_neighbors(b)
        mine_cnt = 0
        uncovered_cnt = 0
        unsolved = [] 
        for adj_block in block:
            if adj_block.status == -2 or adj_block.status == -4:
                mine_cnt = mine_cnt + 1
            elif adj_block.status >= 0:
                uncovered_cnt = uncovered_cnt + 1
            elif adj_block.status == -1:
                unsolved.append(adj_block)
            else:
                #print("Error status in this block:", b.x, b.y
                return
                
        # if all blocks around has a status>=-1, the block is solved
        if mine_cnt + uncovered_cnt == b.adjacent_blocks:
            self.solved.append(b)
            self.frontier.remove(b)
            #print("outer_edge removed",b.x,b.y,mine_cnt,uncovered_cnt)
        
        # if all are solvable (i.e. enough mines flagged around)
        if mine_cnt==b.status:
            for solvable_block in unsolved:
                act = Action(AI.Action.UNCOVER, solvable_block.x, solvable_block.y)
                exist = False
                for sol in self.moves:
                    if sol.getX()==solvable_block.x and sol.getY()==solvable_block.y:
                        exist = True
                if not exist:
                    #print("from",b.x,b.y,"solve",solvable_block.x,solvable_block.y)
                    self.moves.append(act)

        # if all are mines (i.e. all uncovered blocks around are mines)
        if len(unsolved) == b.status-mine_cnt:
            for solvable_block in unsolved:
                act = Action(AI.Action.FLAG, solvable_block.x, solvable_block.y)
                exist = False
                for sol in self.moves:
                    if sol.getX() == solvable_block.x and sol.getY() == solvable_block.y:
                        exist = True
                if not exist:
                    #print("from",b.x,b.y,"solve",solvable_block.x,solvable_block.y)
                    self.moves.append(act)
