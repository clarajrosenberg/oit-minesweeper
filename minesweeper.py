import random
import re
import pygame
import sys
import math

class Board:
    def __init__(self, dim_size, num_bombs, font):
        self.dim_size = dim_size
        self.num_bombs = num_bombs
        self.font = font
        self.square_size = 50
        self.dim = self.dim_size*self.square_size
        self.size = (self.dim, self.dim)
        self.screen = pygame.display.set_mode(self.size)

        # create new board
        self.board = self.make_new_board()
        self.assign_values_to_board()

        # set for uncovered locations
        self.dug = set()

        # set for marked bombs
        self.marked = set()

    def make_new_board(self):
        """
        Create a new board with the given dimensions & plant bombs.
        """
        board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]

        bombs_planted = 0
        while bombs_planted < self.num_bombs:
            loc = random.randint(0, self.dim_size**2 - 1)
            row = loc // self.dim_size
            col = loc % self.dim_size
            if board[row][col] == "*":
                continue
            else:
                board[row][col] = "*"
                bombs_planted += 1
    
        return board
    
    def get_num_neighboring_bombs(self, row, col):
        """
        Helper function for assign_values_to_board()
        Args: row & col board coordinates
        Returns: number of adjacent bombs for a given square
        """
        num_neighboring_bombs = 0
        for r in range(max(0, row-1), min(self.dim_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1)+1):
                if r == row and c == col:
                    continue
                if self.board[r][c] == "*":
                    num_neighboring_bombs += 1
       
        return num_neighboring_bombs

    def assign_values_to_board(self):
        """
        Assign number of adjacent bombs to each non-bomb square.
        """
        for r in range(self.dim_size):
            for c in range(self.dim_size):
                if self.board[r][c] == "*":
                    continue
                else:
                    self.board[r][c] = self.get_num_neighboring_bombs(r, c)

    def dig(self, row, col):
        """
        Dig at clicked location & adjacent recursively until numbers are reached
        Args: row & col board coordinates
        Returns: True if a bomb has been clicked, False otherwise
        """
        self.dug.add((row, col))

        # case 1: clicked square is bomb, game over
        if self.board[row][col] == "*":
            return True
        # case 2: clicked square is adjacent to bomb, show number
        elif self.board[row][col] > 0:
            return False
        # case 3: clicked square is not adjacent to bomb, dig recursively
        else:
            for r in range(max(0, row-1), min(self.dim_size - 1, row+1)+1):
                for c in range(max(0, col-1), min(self.dim_size - 1, col+1)+1):
                    if (r, c) in self.dug:
                        continue
                    self.dig(r, c)
            return False
    
    def mark_bomb(self, row, col):
        """
        Mark the clicked square as a potential bomb
        """
        self.marked.add((row, col))

    def draw_board(self, game_over = False):
        """
        Draw the minesweeper board.
        Args: game_over False by default, True if no more moves
        """
        bombs_found = 0
        for c in range(self.dim_size):
            for r in range(self.dim_size):
                # squares that have been uncovered
                if (r, c) in self.dug:
                    # case 1: bomb, draw red square & dark border
                    if self.board[r][c] == "*":
                        pygame.draw.rect(self.screen, (255, 0, 0), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                        pygame.draw.rect(self.screen, (0, 0, 0), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)
                        bombs_found = 1
                    # case 2: empty, draw white square & light border
                    elif self.board[r][c] == 0:
                        pygame.draw.rect(self.screen, (255, 255, 255), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                        pygame.draw.rect(self.screen, (100, 100, 100), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)
                    # case 3: adjacent to bomb, draw white square w/number & dark border
                    elif self.board[r][c] > 0:
                        pygame.draw.rect(self.screen, (255, 255, 255), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                        pygame.draw.rect(self.screen, (0, 0, 0), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)
                        num_text = str(self.board[r][c])
                        num_image = self.font.render(num_text, True, (0, 0, 0), (255, 255, 255))
                        x_margin = (self.square_size - 1 - num_image.get_width())//2
                        y_margin = (self.square_size - 1 - num_image.get_height())//2
                        self.screen.blit(num_image, (c*self.square_size + 2 + x_margin, r*self.square_size + 2 + y_margin))
                # squares that have been marked as bombs; draw orange square & dark border
                elif (r, c) in self.marked:
                    pygame.draw.rect(self.screen, (255, 99, 71), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                    pygame.draw.rect(self.screen, (0, 0, 0), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)
                # covered & unmarked square; draw gray square & light border
                else:
                    pygame.draw.rect(self.screen, (200, 200, 200), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                    pygame.draw.rect(self.screen, (100, 100, 100), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)
        # game over win mechanism: turn bomb squares green
        if game_over is True:
            if bombs_found == 0:
                for c in range(self.dim_size):
                    for r in range(self.dim_size):
                        if self.board[r][c] == "*":
                            pygame.draw.rect(self.screen, (0, 220, 0), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                            pygame.draw.rect(self.screen, (100, 100, 100), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)

        pygame.display.update()


def play(dim_size = 10, num_bombs = 10):
    # initial values and board
    pygame.init()
    LEFT = 1
    RIGHT = 3
    font = pygame.font.SysFont(None, 24)
    board = Board(dim_size, num_bombs, font)
    game_over = False
    board.draw_board(game_over)

    while not game_over:
        for event in pygame.event.get():
            # game quit mechanism
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # get coordinates
                x_pos = event.pos[0]
                y_pos = event.pos[1]
                col = int(math.floor(x_pos/board.square_size))
                row = int(math.floor(y_pos/board.square_size))
                # left click: dig
                if event.button == 1:
                    if len(board.dug) < board.dim_size ** 2 - num_bombs:
                        game_over = board.dig(row, col)
                        # win game case
                        if len(board.dug) == board.dim_size ** 2 - num_bombs:
                            board.draw_board(game_over = True)
                            game_over = True
                        else:
                            board.draw_board(game_over)
                # right click: mark bomb
                if event.button == 3:
                    board.mark_bomb(row, col)
                    board.draw_board(game_over)
                # wait to close
                if game_over:
                    pygame.time.wait(3000)

if __name__ == "__main__":
    play()