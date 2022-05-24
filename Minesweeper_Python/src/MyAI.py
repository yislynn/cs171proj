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
        # if mined tile is in sentence, remove and decrement mine count
        if tile in self.tiles:
            self.tiles.remove(tile)
            self.count -= 1

    def mark_safe(self, tile):
        if tile in self.tiles:
            self.tiles.remove(tile)
    
    def printSet(self):
        for t in self.tiles:
            print(t, end=", ")
        print(self.count)

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
    
    def flag(self) -> None:
        if self.status < 0:
            self.status = -4
       
    def __str__(self): # f strings only exist in python 3.6; incompatible
        return "Label:{}/ELabel:{}/Status:{}/x:{}/y:{}".format(self.label, self.elabel, self.status, self.x, self.y)

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
        
        # Keep track of which cells have had moves made on them
        self.moves_made = set()
        self.moves_made.add(self.__board[startX][startY]) # add start as a move already made
        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()
        self.safes.add(self.__board[startX][startY]) # add start as a safe tile

        self.knowledge_base = [] # list of all known facts about the game; knowledge, statement_list

        
        self.solved = []
        self.moves = [] # solvable sentences
        self.frontier = []

    ##################################################################################################################
    # Methods
    ##################################################################################################################

    def getAction(self, number: int) -> "Action Object":
        x = self.__prev_move.getX()
        y = self.__prev_move.getY()
        print(number, x, y)
        self.__currX = x # update coordinates of previous moves
        self.__currY = y

        if len(self.mines) == self.__totalMines:
            return Action(AI.Action.LEAVE)

        print("SOLVED:")
        for t in self.solved:
            print(t)

        print("action")
        if number >= 0: # not a flag action
            print("updated")
            self.__board[x][y].uncover(number)             # "uncover"
            self.add_knowledge(self.__board[x][y], number) # add the new information to the knowledge base

            if (not self.__board[x][y] in self.solved) and (not self.__board[x][y] in self.frontier):
                # not a solved tile (all surroundings known) and not in frontier;
                # add to frontier as a tile of interest
                print("add to frontier")
                self.frontier.append(self.__board[x][y])

        else:
            print("flag")
            self.__board[x][y].flag()          # mark as flagged
            self.mark_mine(self.__board[x][y]) # mark as mine in kb

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

    def get_tile_unknown(self, tile):
        """Gets the neighbors that should have mines"""
        n = self.get_neighbors(tile.x, tile.y)
        tiles = []
        for x,y in n:
            if self.__board[x][y].status == -1:
                tiles.append(self.__board[x][y])
        return tiles

    ##################################################################################################################
    def mark_mine(self, tile):
        self.mines.add(tile) # add to set of safe tiles
        tile.status = -2
        # check if already in?
        self.addMove(tile, Action(AI.Action.FLAG,tile.x,tile.y))
        for sentence in self.knowledge_base:
            sentence.mark_mine(tile)

    def mark_safe(self, tile):
        self.safes.add(tile) # add to set of safe tiles
        self.addMove(tile, Action(AI.Action.UNCOVER,tile.x,tile.y))
        for sentence in self.knowledge_base:
            # remove safe tiles from all sentences
            sentence.mark_safe(tile)

    def add_knowledge(self, tile, count):
        # only called if a tile is uncovered/safe
        print("################ ADD KNOWLEDGE")
        print("ADD KNOWLEDGE IS CURRENTLY WORKING WITH TILE", tile)
        
        # updating status information
        self.moves_made.add(tile) # add to moves made
        self.mark_safe(tile)      # mark as safe (remove from rules); the tile is safe
        tile.status = count       # change label to the uncovered mine value

        new_kb = []
        # check for empty sentences and remove them
        for s in self.knowledge_base:
            if len(s.tiles) != 0:
                new_kb.append(s)
        self.knowledge_base = new_kb

        # create new sentence and add it to the knowledge base, if possible
        tiles = self.get_tile_neighbors(tile) # get neighbors;
        sentence = Sentence(tiles, count)
        for tile in tiles:
            if tile in self.safes:
                sentence.mark_safe(tile)
            if tile in self.mines:
                sentence.mark_mine(tile)

        if sentence not in self.knowledge_base:
            self.knowledge_base.append(sentence)     # add to knowledge base if not already in there
        
        print("KNOWLEDGE BASE:")
        for stmt in self.knowledge_base:
            stmt.printSet()
        print("KNOWLEDGE BASE")

        print("adding:")
        s.printSet()

        print("SOLVED LIST:")
        for t in self.solved:
            print(t)
        print("END OF SOLVED LIST")
        
        print("THE NEW SENTENCE IS SOLVEABLE?", self.isSolveable(s))
        print("THE TILE IS IN SOLVED LIST?", tile in self.solved)

        # check if the sentence is solveable
        if len(sentence.tiles) == 0:
            print("The tile neighborhood was conmpletely filled with safe/mine tiles")
            self.knowledge_base.remove(sentence)
            print("Removed the empty sentence from the kb")
        elif self.isSolveable(sentence) and tile not in self.solved:
            print("solveable")
            # if the tile is solveable (surroundings known) and the tile is not solved: 
            if sentence.count == 0:                  # case one: there are no mines
                self.knowledge_base.remove(s) # remove from knowledge base (provides no additional information)
                ti = list(sentence.tiles)            # get the tiles
                for t in ti:
                    self.mark_safe(t)         # mark all tiles in the list as safe
                    print("Adding to moves (add to kb safe tiles)")
                if tile not in self.solved:
                    print("Adding", tile, "to solved")
                    self.solved.append(tile)  # add the tile as a known solved tile (all neighbors are safe)
                if tile in self.frontier:
                    self.frontier.remove(tile)
            
            else:                             # case 2: all tiles in the set are mines
                ti = list(sentence.tiles)
                for t in ti:
                    self.mark_mine(t)         # mark all tiles as mines
                    print("Adding to moves (add to kb mine tiles)")
                if tile not in self.solved:
                    print("Adding", tile, "to solved")
                    self.solved.append(tile) # add the tile as a known solved tile (all neighbors are mines)
                if tile in self.frontier:
                    self.frontier.remove(tile)
        ######################################################################## EXTRANEOUS?
        print("double checking")
        new_kb = []
        for s in self.knowledge_base:
            # double check knowledge base after adding new sentence
            solveable = self.isSolveable(s)
            if solveable and tile not in self.solved:
                # if the tile is solveable (surroundings known) and the tile is not solved
                if s.count == 0:                 # Case 1: there are no mines
                    ti = list(s.tiles)
                    for t in ti:
                        self.mark_safe(t)        # mark all tiles as safe
                        print("Adding to moves (add to kb safe tiles)")
                    if tile not in self.solved:
                        print("Adding", tile, "to solved")
                        self.solved.append(tile) # add the tile as a known solved tile
                    if tile in self.frontier:
                        self.frontier.remove(tile)
                else:                            # Case 2: all tiles in the set are mines
                    new_kb.append(s)             # add to new kb
                    ti = list(s.tiles)
                    for t in ti:
                        self.mark_mine(t)        # mark all tiles as mines
                        print("Adding to moves (add to kb mine tiles)")
                    if tile not in self.solved:
                        print("Adding", tile, "to solved")
                        self.solved.append(tile) # add the tile as a known solved tile
                    if tile in self.frontier:
                        self.frontier.remove(tile)
            elif not solveable:
                # the tile is not solveable. add to new kb
                new_kb.append(sentence)
        self.knowledge_base = new_kb

        print("solving statements")
        self.solve_statements(sentence)

    def make_safe_move(self):
        print("moves:")
        for move in self.moves:
            if move.getMove() == AI.Action.UNCOVER:
                print("{} at {}, {}".format("UNCOVER", move.getX(), move.getY()))
            elif move.getMove() == AI.Action.FLAG:
                print("{} at {}, {}".format("FLAG", move.getX(), move.getY()))
            elif move.getMove() == AI.Action.LEAVE:
                print("{} at {}, {}".format("LEAVE", move.getX(), move.getY()))
        print("find a move")
        
        if not self.moves: # if move list empty make inferences
            print("solving statements")
            self.solve_statements()

        if not self.moves: # if move list empty search frontier
            self.find_move()

        if not self.moves: # if move list empty make a random guess
            print("make a guess")
            self.make_guess()

        # get a move
        print("MOVES HAS LEN", len(self.moves))
        next_move = self.moves.pop(0)
        print("get a move")
        self.__prev_move = next_move
        print("returning")
		#print("visit",next_move.getX(),next_move.getY(),next_move.getMove())
        return next_move

######################################################################################################################
    def minus(self, left, right):
        if left.tiles.issubset(right.tiles) and len(left.tiles) > 0 and left.tiles != right.tiles:
            return Sentence(right.tiles - left.tiles, right.count - left.count)
        else:
            return None

    def isSolveable(self, stmt) -> bool:
        if len(stmt.tiles) == 0: # must be at least 1 element in list
            print("No tiles in the list")
            return False
        # there are no mines in the tile list or
        # all tiles are mines
        if stmt.count == 0:
            print("NO MINES")
            return True
        elif len(stmt.tiles) == stmt.count:
            print("all mines!!!!")
            return True
        print("NOT SOLVEABLE")
        return False

    def solve_statements(self, sentence):
        print("solving statements start")

        for safe in self.safes: # (not at the beginning so that it doesnt result in empty tile lists)
            # periodically remove the safe tiles
            self.mark_safe(safe)

        # for mine in self.mines:
        #     # periodically mark the mine tiles
        #     self.mark_mine(mine)

        infer_list = []
        gen_new = True
        while gen_new:
            print("inloop")
            gen_new = False
            new_stmts = []
            for right in self.knowledge_base:
                if sentence != right:
                    # print("not the same")
                    new_s = self.minus(sentence, right)
                    # print("get new")
                    #left.printSet()
                    #right.printSet()
                    if new_s != None and len(new_s.tiles) > 0 and new_s not in self.knowledge_base:	# gen a new & diff statement (and valid)
                        print("NEWLY GEN STATEMENT:")
                        new_s.printSet()
                        # print("generated new statement that isnt in the knowledge base")
                        if self.isSolveable(new_s):
                            # print("new_s is solveable")
                            if new_s not in infer_list:
                                # print("appending")
                                infer_list.append(new_s)
                        else:
                            # print("not solveable")
                            if (new_s not in self.knowledge_base) and (new_s not in new_stmts):
                                # print("not in knowledge base, or in new statements")
                                print("GENERATED:")
                                new_s.printSet()

                                for tile in new_s.tiles:
                                    if tile in self.safes:
                                        s.mark_safe(tile)
                                    if tile in self.mines:
                                        s.mark_mine(tile)
                                if len(new_s.tiles) != 0:
                                    new_stmts.append(new_s)

                                # print("gen new")
                                gen_new = True
                    new_s = self.minus(right, sentence)
                    # print("get new")
                    #left.printSet()
                    #right.printSet()
                    if new_s != None and len(new_s.tiles) > 0 and new_s not in self.knowledge_base:	# gen a new & diff statement (and valid)
                        print("NEWLY GEN STATEMENT:")
                        new_s.printSet()
                        # print("generated new statement that isnt in the knowledge base")
                        if self.isSolveable(new_s):
                            # print("new_s is solveable")
                            if new_s not in infer_list:
                                # print("appending")
                                infer_list.append(new_s)
                        else:
                            # print("not solveable")
                            if (new_s not in self.knowledge_base) and (new_s not in new_stmts):
                                # print("not in knowledge base, or in new statements")
                                print("GENERATED:")
                                new_s.printSet()

                                for tile in new_s.tiles:
                                    if tile in self.safes:
                                        s.mark_safe(tile)
                                    if tile in self.mines:
                                        s.mark_mine(tile)
                                if len(new_s.tiles) != 0:
                                    new_stmts.append(new_s)

                                # print("gen new")
                                gen_new = True
            print("extend")
            self.knowledge_base.extend(new_stmts)
        print("while loop end")

        for s in infer_list:
            if s.count == 0:
                for tile in s.tiles:
                    self.mark_safe(tile)
                    print("Adding to moves (inferred new statements = safe)")
                if tile not in self.solved:
                    print("Adding", tile, "to solved")
                    self.solved.append(tile)
                if tile in self.frontier:
                    self.frontier.remove(tile)
            elif len(s.tiles)==s.count:
                for tile in s.tiles:
                    self.mark_mine(tile)
                    print("Adding to moves (inferred new statements = mines)")
                if tile not in self.solved:
                    print("Adding", tile, "to solved")
                    self.solved.append(tile)
                if tile in self.frontier:
                    self.frontier.remove(tile)

    def find_move(self) -> None:
        """Find a possible move by searching the frontier"""
        print("Searching frontier")
        for tile in self.frontier:
            print(tile)
            self.solve_tile(tile)

    def make_guess(self) -> None:
        """Choose a random tile to uncover and append it to the moves list"""
        print("make a random move")
        # get a sentence from the knowledge base and choose one of the tiles to uncover
        if len(self.knowledge_base) > 0:
            moveset = sorted(self.knowledge_base, key=lambda x: len(x.tiles), reverse=True)
            moveset = sorted(moveset, key=lambda x: x.count)

            moves = moveset[0].tiles
            if (len(moves) != 0):
                move = random.choice(list(moves))
                self.addMove(move, Action(AI.Action.UNCOVER,move.x,move.y))
            return

        print("In make guess")
        unsolved = [] # list of unknowns
        print(self.__rows, self.__cols)
        for x in range(0, self.__rows):
            for y in range(0, self.__cols):
                print("checkin time")
                if self.__board[x][y].status == -1 or (self.__board[x][y].status == -1 and self.__board[x][y] not in self.moves_made):
                    print("found an unknown")
                    unsolved.append((x, y))
        print("got the unknowns (make guess)")
        if len(unsolved) > 0:
            (x,y) = random.choice(unsolved)
            print("Adding to moves (made a guess):", x, y)
            self.addMove(self.__board[x][y], Action(AI.Action.UNCOVER, x, y))
            return
        else:
            if len(self.mines) == self.__totalMines:
                self.moves.append(Action(AI.Action.LEAVE))
        return

    def solve_tile(self, t) -> None:
        if t.status <= -1: # only solve uncovered tiles
            # check how many blocks around are solved or are mines.
            flagged = self.get_tile_mines(t)
            unknown = self.get_tile_unknown(t)

            if t.label == len(flagged):
                if t not in self.solved:
                    print("Adding", tile, "to solved")
                    self.solved.append(t) # add the tile as a known solved tile
                if tile in self.frontier:
                    self.frontier.remove(t)
                self.frontier.remove(t)
                for tile in unknown:
                    self.mark_safe(tile)

            if t.label == len(unknown):
                if t not in self.solved:
                    print("Adding", tile, "to solved")
                    self.solved.append(t) # add the tile as a known solved tile
                self.frontier.remove(t)
                for tile in unknown:
                    self.mark_mine(tile)
                if tile in self.frontier:
                    self.frontier.remove(t)

    def addMove(self, tile, action):
        # print("MOVE MADE")
        # for t in self.moves_made:
        #     print(t)
        # print("END OF MOVES MADE")
        if tile not in self.moves_made:
            print("A move has not yet been made on tile", tile)
            if action not in self.moves:
                self.moves_made.add(tile)
                self.moves.append(action)
