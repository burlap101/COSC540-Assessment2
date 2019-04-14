import numpy as np
import random
import os

class BattleShips():

    def __init__(self, rows=9, columns=9):
        self.ships = [
            ('A',2),
            ('L',3),
            ('H',4),
            ('C',5),
        ]

        alphabet = 'abcdefghijklmnopqrstuvwxyz'.upper()
        self.cols = alphabet[:columns]
        self.rows = [x for x in range(rows+1)]
        self.board = np.zeros((rows, columns))
        self._running = False
        self.hit_count = 0
        self.turns_taken = 0

    def _validate_coords(self, coords):
        try:
            if (coords[0] in self.cols) and (int(coords[1:])-1 in self.rows):
                return True
            else:
                return False
        except ValueError:
            return False

    def ready(self):
        return self.ready_flag

    def running(self):
        return self._running

class ClientGame(BattleShips):

    def print_board(self):
        row_buf = [x for x in self.cols]
        print(' ',' '.join(row_buf))
        for row in np.arange(0,9,1):
            row_buf=[]
            for space in np.nditer(self.board[row,:]):
                space = int(space)
                if space==0:
                    row_buf.append('.')
                elif space == -1:
                    row_buf.append('O')
                elif space == -2:
                    row_buf.append('X')

            print(row+1, ' '.join(row_buf))

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
                self._running = False
            return 'HIT'

class ServerGame(BattleShips):

    def setup_ship_placement(self):
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
            self._running = True

    def print_board(self):
        row_buf = [x for x in self.cols]
        print(' ',' '.join(row_buf))
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

            print(row+1, ' '.join(row_buf))

    def shot_fired(self, coords):
        if self._validate_coords(coords):
            row = int(coords[1])-1
            col = self.cols.index(coords[0])
        else:
            return False

        if self.board[row,col] <= 0:
            self.board[row, col] = -1
            return 'MISS'
        elif self.board[row,col] > 0:
            self.board[row, col] = -2
            self.hit_count += 1
            if self.hit_count >= 14:
                self._running = False
            return 'HIT'
