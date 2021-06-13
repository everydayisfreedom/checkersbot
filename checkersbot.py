'''
Tutorial followed: Tech by Tim - Checkers

Required package to be installed: pygame
What is pygame for?
Pygame is a cross-platform set of Python modules designed for writing video games.
Use the pip install pygame command to install it. 
'''
import pygame
from copy import deepcopy
from datetime import datetime
##########################################################
'''CONSTANTS'''

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8 #Columns and rows: standard checkers board is 8x8

#Square size of each checker slot
SQUARE_SIZE = int(WIDTH/COLS)

#Colors to be used: I picked a pink and white scheme (RGB color codes)
LIGHTPINK 		= (255,182,193) 
FLORALWHITE 	= (255,250,240)
CRIMSON 		= (220,20,60)
GOLD 			= (255,193,37)
PINKOUTLINE 	= (205,140,149)
WHITEOUTLINE 	= (211,211,211)
BLACK 			= (0,0,0)
##########################################################
##########################################################
'''Piece'''

class Piece:
    BORDER, OUTLINE  = 15, 3

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + int(SQUARE_SIZE/2)
        self.y = SQUARE_SIZE * self.row + int(SQUARE_SIZE/2)

    def make_king(self):
        self.king = True
    
    def draw(self, win):
        radius = int(SQUARE_SIZE/2) - self.BORDER
        outercolor = PINKOUTLINE if self.color == LIGHTPINK else WHITEOUTLINE
        pygame.draw.circle(win, outercolor, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
        	pygame.draw.circle(win, GOLD, (self.x, self.y), radius/2)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return str(self.color)

##########################################################
'''Board'''

class Board:
	def __init__(self):
		self.board = [] #Creating the pieces object in a 2D list with rows and columns
		self.selected_piece = None #Have we selected a piece? We need to keep track of that
		self.pink_left = self.white_left = 12 #How many pink and white pieces do we have?
		self.pink_kings = self.white_kings = 0
		self.create_Board()

	#Draw the board
	def draw_square(self, win):
		win.fill(FLORALWHITE) #background color is white
		dimension = lambda r,c: (r*SQUARE_SIZE, c*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
		draw_squares = [pygame.draw.rect(win, LIGHTPINK, dimension(row,col)) for row in range(ROWS) for col in range(row%2, ROWS, 2)]

	def move(self, piece, row, col):
		self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
		piece.move(row, col)
		if row in [ROWS - 1, 0]:
			piece.make_king()
			self.white_kings += 1 if piece.color == FLORALWHITE else self.pink_kings+1

	def get_piece(self, row, col):
		return self.board[row][col]

	def evaluate(self):
		return self.white_left - self.pink_left + (self.white_kings - self.pink_kings)/2

	def get_all_pieces(self, color):
		pieces = []
		for row in self.board:
			for piece in row:
				if piece != 0 and piece.color == color:
					pieces.append(piece)
		return pieces


	def create_Board(self):
		ranges = { **dict.fromkeys([1, 2, 0], FLORALWHITE), **dict.fromkeys([5, 6, 7], LIGHTPINK) }
		for row in range(ROWS):
			self.board.append([])
			for col in range(COLS):
				self.board[row].append(Piece(row,col,ranges[row])) if row in ranges and col%2 == ((row +1) % 2) else self.board[row].append(0)

	def draw(self,win):
		self.draw_square(win)
		for row in range(ROWS):
			for col in range(COLS):
				piece = self.board[row][col]
				if piece != 0:
					piece.draw(win)

	def remove(self, pieces):
		for piece in pieces:
			self.board[piece.row][piece.col] = 0
			if piece != 0:
				if piece.color == LIGHTPINK:
					self.pink_left -= 1
				else:
					self.white_left -= 1
    
	def winner(self):
		if self.pink_left <= 0:
			return "You lost :(. Better Luck next time!"
		elif self.white_left <= 0:
			return "You won :) !"
		return None 

	def get_valid_moves(self, piece):
		moves = {}
		left = piece.col - 1
		right = piece.col + 1
		row = piece.row

		if piece.color == LIGHTPINK or piece.king:
			moves.update(self._traverse_left(row -1, max(row-3, -1), -1, piece.color, left))
			moves.update(self._traverse_right(row -1, max(row-3, -1), -1, piece.color, right))
		
		if piece.color == FLORALWHITE or piece.king:
			moves.update(self._traverse_left(row +1, min(row+3, ROWS), 1, piece.color, left))
			moves.update(self._traverse_right(row +1, min(row+3, ROWS), 1, piece.color, right))

		return moves

	def _traverse_left(self, start, stop, step, color, left, skipped=[]):
		moves = {}
		last = []
		for r in range(start, stop, step):
			if left < 0:
				break

			current = self.board[r][left]
			if current == 0:
				if skipped and not last:
				    break
				elif skipped:
				    moves[(r, left)] = last + skipped
				else:
				    moves[(r, left)] = last

				if last:
				    row = max(r-3, 0) if step == -1 else min(r+3, ROWS)
				    moves.update(self._traverse_left(r+step, row, step, color, left-1,skipped=last))
				    moves.update(self._traverse_right(r+step, row, step, color, left+1,skipped=last))
				break
			elif current.color == color:
				break
			else:
				last = [current]

			left -= 1

		return moves

	def _traverse_right(self, start, stop, step, color, right, skipped=[]):
		moves = {}
		last = []
		for r in range(start, stop, step):
			if right >= COLS:
				break

			current = self.board[r][right]

			if current == 0:
				if skipped and not last:
				    break
				elif skipped:
				    moves[(r,right)] = last + skipped
				else:
				    moves[(r, right)] = last

				if last:
				    row = max(r-3, 0) if step == -1 else min(r+3, ROWS)
				    moves.update(self._traverse_left(r+step, row, step, color, right-1,skipped=last))
				    moves.update(self._traverse_right(r+step, row, step, color, right+1,skipped=last))
				break
			elif current.color == color:
				break
			else:
				last = [current]

			right += 1

		return moves

##########################################################
'''Game'''

class Game:
    def __init__(self, win):
        self._init()
        self.win = win
    
    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = LIGHTPINK
        self.valid_moves = {}

    def winner(self):
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
            
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, CRIMSON, (col * SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 15)

    def change_turn(self):
        self.valid_moves = {}
        self.turn = FLORALWHITE if self.turn == LIGHTPINK else LIGHTPINK

    def get_board(self):
        return self.board

    def ai_move(self, board):
        self.board = board
        self.change_turn()

##########################################################
##########################################################
'''minimax algorithm for the bot'''
def minimax(position, depth, max_player, game):
    if depth == 0 or position.winner() != None:
        return position.evaluate(), position
    
    if max_player:
        maxEval = float('-inf')
        best_move = None
        for move in get_all_moves(position, FLORALWHITE, game):
            evaluation = minimax(move, depth-1, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
        
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(position, LIGHTPINK, game):
            evaluation = minimax(move, depth-1, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
        
        return minEval, best_move


def simulate_move(piece, move, board, game, skip):
    board.move(piece, move[0], move[1])
    if skip:
        board.remove(skip)
    return board


def get_all_moves(board, color, game):
    moves = []
    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            print_moves(game,board,piece)
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, game, skip)
            moves.append(new_board)
    return moves

def print_moves(game, board, piece):
    valid_moves = board.get_valid_moves(piece)
    print("Considered moves at\t", datetime.now(), "\t", *valid_moves)

##########################################################
##########################################################

def get_row_col_from_mouse(pos):
    x, y = pos
    col, row = int(x/SQUARE_SIZE),int(y/SQUARE_SIZE)
    return row, col

def winning_popup(strx):
	import pygame
	pygame.init()
	X,Y = 600, 200

	display_surface = pygame.display.set_mode((X, Y))
	pygame.display.set_caption('Who won the game?')

	font = pygame.font.Font('freesansbold.ttf', 25)
	text = font.render(strx, True, CRIMSON)

	textRect = text.get_rect()
	textRect.center = (X // 2, Y // 2)

	while True:
		display_surface.fill(FLORALWHITE)
		display_surface.blit(text, textRect)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			pygame.display.update()


WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers Game')

def checkersgame():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(60) #60 frame per second
        if game.turn == FLORALWHITE:
            value, new_board = minimax(game.get_board(), 1, FLORALWHITE, game)
            pygame.time.delay(100)
            game.ai_move(new_board)

        if game.winner() != None:
            print(game.winner())
            run = False
            winning_popup(game.winner())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)

        game.update()
    pygame.quit()

checkersgame()

