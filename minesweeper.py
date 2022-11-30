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

        # create board
        self.board = self.make_new_board()
        self.assign_values_to_board()

        # keep track of uncovered locations
        self.dug = set()

        # keep track of marked bombs
        self.marked = set()

    def make_new_board(self):
        board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]

        bombs_planted = 0
        while bombs_planted < self.num_bombs:
            loc = random.randint(0, self.dim_size**2 - 1)
            row = loc // self.dim_size
            col = loc % self.dim_size

            if board[row][col] == "*":
                continue
            
            board[row][col] = "*"
            bombs_planted += 1
        
        return board

    def assign_values_to_board(self):
        for r in range(self.dim_size):
            for c in range(self.dim_size):
                if self.board[r][c] == "*":
                    continue
                self.board[r][c] = self.get_num_neighboring_bombs(r, c)

    def get_num_neighboring_bombs(self, row, col):
        num_neighboring_bombs = 0
        for r in range(max(0, row-1), min(self.dim_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1)+1):
                if r == row and c == col:
                    continue
                if self.board[r][c] == "*":
                    num_neighboring_bombs += 1
        
        return num_neighboring_bombs

    def dig(self, row, col):
        self.dug.add((row, col))

        if self.board[row][col] == "*":
            return False
        elif self.board[row][col] > 0:
            return True
        
        for r in range(max(0, row-1), min(self.dim_size - 1, row+1)+1):
            for c in range(max(0, col-1), min(self.dim_size - 1, col+1)+1):
                if (r, c) in self.dug:
                    continue
                self.dig(r, c)
        
        return True
    
    def mark_bomb(self, row, col):
        self.marked.add((row, col))

    def draw_board(self, game_over):
        bombs_found = 0
        for c in range(self.dim_size):
            for r in range(self.dim_size):
                if (r, c) in self.dug:
                    if self.board[r][c] == "*":
                        pygame.draw.rect(self.screen, (220, 0, 0), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                        pygame.draw.rect(self.screen, (0, 0, 0), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)
                        bombs_found = 1
                    elif self.board[r][c] == 0:
                        pygame.draw.rect(self.screen, (255, 255, 255), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                        pygame.draw.rect(self.screen, (100, 100, 100), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)
                    elif self.board[r][c] > 0:
                        pygame.draw.rect(self.screen, (255, 255, 255), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                        pygame.draw.rect(self.screen, (0, 0, 0), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)
                        num_text = str(self.board[r][c])
                        num_image = self.font.render(num_text, True, (0, 0, 0), (255, 255, 255))
                        x_margin = (self.square_size - 1 - num_image.get_width())//2
                        y_margin = (self.square_size - 1 - num_image.get_height())//2
                        self.screen.blit(num_image, (c*self.square_size + 2 + x_margin, r*self.square_size + 2 + y_margin))
                elif (r, c) in self.marked:
                    pygame.draw.rect(self.screen, (255, 99, 71), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                    pygame.draw.rect(self.screen, (0, 0, 0), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)
                else:
                    pygame.draw.rect(self.screen, (200, 200, 200), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                    pygame.draw.rect(self.screen, (100, 100, 100), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)
        if game_over is True:
            if bombs_found == 0:
                for c in range(self.dim_size):
                    for r in range(self.dim_size):
                            if self.board[r][c] == "*":
                                pygame.draw.rect(self.screen, (0, 220, 0), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
                                pygame.draw.rect(self.screen, (100, 100, 100), (c*self.square_size, r*self.square_size, self.square_size, self.square_size), width = 1)

        
        pygame.display.update()


def play(dim_size = 10, num_bombs = 10):
    pygame.init()
    LEFT = 1
    RIGHT = 3
    font = pygame.font.SysFont(None, 24)
    board = Board(dim_size, num_bombs, font)
    safe = True
    game_over = False
    board.draw_board(game_over)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos = event.pos[0]
                y_pos = event.pos[1]
                col = int(math.floor(x_pos/board.square_size))
                row = int(math.floor(y_pos/board.square_size))
                if event.button == 1:
                    if len(board.dug) < board.dim_size ** 2 - num_bombs:
                        safe = board.dig(row, col)
                        if not safe:
                            game_over = True
                        if len(board.dug) == board.dim_size ** 2 - num_bombs:
                            board.draw_board(game_over = True)
                            game_over = True
                        else:
                            board.draw_board(game_over)
                if event.button == 3:
                    board.mark_bomb(row, col)
                    board.draw_board(game_over)
                if game_over:
                    pygame.time.wait(3000)

if __name__ == "__main__":
    play()