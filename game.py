# Classes for handling game logic. BattleShips is common game functionality
# between client and server. ClientGame is client specific methods and attributes
# ServerGame is server specific methods and attributes.
#
#
#
#

import numpy as np
import random
import os, sys


class BattleShips():

    def __init__(self, rows=9, columns=9):
        # Could expand the board if desired by entering arguments at object instantiation
        self.ships = [
            ('A',2),
            ('L',3),
            ('H',4),
            ('C',5),
        ]   # list of tuples to represent the ships.

        alphabet = 'abcdefghijklmnopqrstuvwxyz'.upper()
        self.cols = alphabet[:columns]
        self.rows = [x for x in range(rows+1)]
        self.board = np.zeros((rows, columns))
        self.running = False
        self.hit_count = 0
        self.turns_taken = 0

    def print_board(self, file=sys.stdout):
        row_buf = [x for x in self.cols]
        print(' ',' '.join(row_buf), file=file, flush=True)
        for row in np.arange(0,9,1):
            row_buf=[]
            for space in np.nditer(self.board[row,:]):
                space = int(space)
                if space==0:
                    row_buf.append('.')
                elif space > 0:
                    row_buf.append(self.ships[space-1][0])
                elif space == -1:
                    row_buf.append('O')
                elif space == -2:
                    row_buf.append('X')

            print(row+1, ' '.join(row_buf), file=file, flush=True)

    def _validate_coords(self, coords):
        try:
            if (coords[0] in self.cols) and (int(coords[1:])-1 in self.rows):
                return True
            else:
                return False
        except (ValueError, IndexError):
            return False

    def ready(self):
        return self.ready_flag


class ClientGame(BattleShips):

    def __init__(self):
        super().__init__()
        self.running = True

    # this method validates response from server and updates board client side.
    def shot_fired(self, coords, result):
        if self._validate_coords(coords):
            row = int(coords[1])-1
            col = self.cols.index(coords[0])
            self.turns_taken += 1
        else:
            return False

        if result[:4]=='MISS' and self.board[row,col]==0:
            self.board[row,col] = -1
        elif result[:3]=='HIT' and self.board[row,col]==0:
            self.board[row,col] = -2
            self.hit_count += 1
            if self.hit_count >= 14:
                self.running = False

        return True


class ServerGame(BattleShips):

    def __init__(self):
        super().__init__()
        self.initialised = False
        self.positioning = False

    def setup_ship_placement(self):   # randomly place ships on board
        self.initialised = True
        random.seed()
        orientations = ['V','H']
        for ship,length in self.ships:
            assigned=False
            while not assigned:
                row = random.choice(np.arange(0,len(self.rows),step=1))
                col = random.choice(np.arange(0,len(self.cols),step=1))
                orient = random.choice(orientations)
                try:
                    if orient=='H' and (col+length) <= 9:
                        if np.sum(self.board[row,col:col+length])==0:
                            self.board[row,col:col+length]=self.ships.index((ship,length))+1
                            assigned=True
                    elif orient=='V' and (row+length) <= 9:
                        if np.sum(self.board[row:row+length,col])==0:
                            self.board[row:row+length,col]=self.ships.index((ship,length))+1
                            assigned=True
                except IndexError as e:
                    pass
            self.running = True

    def shot_fired(self, coords):
        if self._validate_coords(coords):
            row = int(coords[1])-1
            col = self.cols.index(coords[0])
            self.turns_taken += 1
        else:
            return False

        if self.board[row,col] <= 0:
            self.board[row, col] = -1
            return 'MISS'
        elif self.board[row,col] > 0:
            self.board[row, col] = -2
            self.hit_count += 1
            if self.hit_count >= 14:
                self.running = False
            return 'HIT'
