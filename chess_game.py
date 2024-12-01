# UI imports
import pygame

# Game Engine Import
import numpy as np
from dataclasses import dataclass

# C O N S T A N T    V A R I A B L E S

# Screen
WIDTH = 800
HEIGHT = 800
SCREEN_DIMENSION = 800

# Board
BOARD_DIMENSION = 8
ROWS = 8
COLUMNS = 8

# Pygame
SQUARE_SIZE = SCREEN_DIMENSION // BOARD_DIMENSION
MAX_FPS = 15
IMAGES = {}





# G A M E   E N G I N E


class Game_State:

    def __init__(self):
        self.board = np.array([
        ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],  
        ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],  
        ['--', '--', '--', '--', '--', '--', '--', '--'],  
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],  
        ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']   
    ])

        self.white_turn = True
        self.move_log = [] 
        self.check_mate = False
        self.stale_mate = False
        self.white_king_coordinates = (7,4) 
        self.black_king_coordinates = (0,4) 
        self.king_in_check = False
        self.enpassant_square_possible_coordinates = ()         # co ordinates for the square where en passant capture is possible

    # Moving a piece
    def move_piece(self, move):
        self.board[move.row1][move.col1] = '--'
        self.board[move.row2][move.col2] = move.piece_moved

        # loging in the move
        self.move_log.append(move)

        # nigga turn / switch the turn
        self.white_turn = not self.white_turn

        # King location update
        if(move.piece_moved == 'wK'):
            self.white_king_coordinates = (move.row2, move.col2)
        if(move.piece_moved == 'bK'):
            self.black_king_coordinates = (move.row2, move.col2)

        # Pawn promotion
        if(move.pawn_promotion):
            self.board[move.row2][move.col2] = move.piece_moved[0] + 'Q'

    # Un-Do
    def undo(self):

        if(len(self.move_log) != 0):
            move = self.move_log.pop()
            self.board[move.row1][move.col1] = move.piece_moved
            self.board[move.row2][move.col2] = move.piece_captured
            self.white_turn = not self.white_turn

            # King location update
            if(move.piece_moved == 'wK'):
                self.white_king_coordinates = (move.row1, move.col1)
            if(move.piece_moved == 'bK'):
                self.black_king_coordinates = (move.row1, move.col1)

    # All the valid moves
    # Valid Moves = All Possible Moves - Moves that can lead the king to be checked directly,
    # without the opposition playing its turn
    def valid_moves_generator(self):
        # 1. generate all moves
        valid_moves = self.all_moves_generator()

        # 2. for each move make a move
        for i in range(len(valid_moves) - 1, -1, -1):
            self.move_piece(valid_moves[i])

            # 3. Generate all opponents move
            # 4. If they attack my king

            self.white_turn = not self.white_turn

            # 5. Attack the king and so remove the move
            if self.in_check():
                valid_moves.remove(valid_moves[i])

            self.white_turn = not self.white_turn
            self.undo()

        if(len(valid_moves) == 0):
            if self.in_check():
                self.check_mate = True
            else:
                self.stale_mate = False
        else:
            self.check_mate = False
            self.stale_mate = False

        return valid_moves

    # Check 
    def in_check(self):
        if(self.white_turn):
            return self.square_under_attack(self.white_king_coordinates[0], self.white_king_coordinates[1])
        else:
            return self.square_under_attack(self.black_king_coordinates[0], self.black_king_coordinates[1])

    # Checking each square for black every move
    def square_under_attack(self, row, col):
        self.white_turn = not self.white_turn
        enemy_move = self.all_moves_generator()
        self.white_turn = not self.white_turn

        for move in enemy_move:
            if move.row2 == row and move.col2 == col:
                return True
        return False
            
        

    # All moves that are possible
    def all_moves_generator(self):
        every_possible_moves = []                   # All moves to be stored in a list

        for row in range(ROWS):
            for col in range(COLUMNS):

                color = self.board[row][col][0]     # w = white, b = black, - = empty

                if(color == 'w' and self.white_turn) or (color == 'b' and not self.white_turn):
                    piece = self.board[row][col][1]
                                                    # All Moves for each piece
                    # Pawn
                    if(piece == 'P'):
                        self.pawn_moves_generator(row, col, every_possible_moves)
                    # Rook
                    elif(piece == 'R'):
                        self.rook_moves_generator(row, col, every_possible_moves)
                    # KNight
                    elif(piece == 'N'):
                        self.kNight_moves_generator(row, col, every_possible_moves)
                    # Bishop
                    elif(piece == 'B'):
                        self.bishop_moves_generator(row, col, every_possible_moves)
                    # Queen
                    elif(piece == 'Q'):
                        self.queen_moves_generator(row, col, every_possible_moves)
                    # King
                    elif(piece == 'K'):
                        self.king_moves_generator(row, col, every_possible_moves)
                    # else:
                    #     continue

        return every_possible_moves

    # P A W N   M O V E S   Generator
    def pawn_moves_generator(self, row, col, every_possible_moves):

        if(self.white_turn): # White turn

            # One square forward
            if(self.board[row-1][col] == '--'):
                every_possible_moves.append(Move((row, col), (row-1, col), self.board))
                # Two square forward.. A one time case
                if(row == 6 and self.board[row-2][col] == '--'):  # We are using nested if because the two square advance move will be from the same start square
                    every_possible_moves.append(Move((row, col), (row-2, col), self.board))
            
            # Capture

            # left diagonal direction
            if(col - 1 >= 0):
                if(self.board[row-1][col-1][0] == 'b'):     # Enenmy
                    every_possible_moves.append(Move((row, col), (row-1, col-1), self.board))
                elif((row-1, col-1) == self.enpassant_square_possible_coordinates):
                    every_possible_moves.append(Move((row, col), (row-1, col-1), self.board, is_enpassant_move = True))

            # right diagonal direction
            if(col + 1 < COLUMNS):
                if(self.board[row-1][col+1][0] == 'b'):
                    every_possible_moves.append(Move((row, col), (row-1, col+1), self.board))
                elif((row-1, col+1) == self.enpassant_square_possible_coordinates):
                    every_possible_moves.append(Move((row, col), (row-1, col+1), self.board, is_enpassant_move = True))

        else:   # Black Turn
            if(self.board[row+1][col] == '--'):
                every_possible_moves.append(Move((row, col), (row+1, col), self.board))
                if(row == 1 and self.board[row+2][col] == '--'):  
                        every_possible_moves.append(Move((row, col), (row+2, col), self.board))
            
            if(col - 1 >= 0):
                if(self.board[row+1][col-1][0] == 'w'):   
                    every_possible_moves.append(Move((row, col), (row+1, col-1), self.board))
                elif((row+1, col-1) == self.enpassant_square_possible_coordinates):
                    every_possible_moves.append(Move((row, col), (row+1, col-1), self.board, is_enpassant_move = True))
                
            if(col + 1 < COLUMNS):
                if(self.board[row+1][col+1][0] == 'w'): 
                    every_possible_moves.append(Move((row, col), (row+1, col+1), self.board))
                elif((row+1, col+1) == self.enpassant_square_possible_coordinates):
                    every_possible_moves.append(Move((row, col), (row+1, col+1), self.board, is_enpassant_move = True))

    # R O O K   M O V E S   Generator
    def rook_moves_generator(self, row, col, every_possible_moves):

        # Up, Down, Left, Right
        direction = ((-1,0), (1,0), (0,-1), (0,1))

        for d in direction:

            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                # Check for boundation
                if(0 <= end_row < ROWS and 0 <= end_col < COLUMNS):
                    piece_at_destination = self.board[end_row][end_col]
                    
                    # Empty square (One at a time)
                    if piece_at_destination == '--': 
                        every_possible_moves.append(Move((row, col), (end_row, end_col), self.board))
                    # Enemy piece
                    elif ((self.white_turn and piece_at_destination[0] == 'b') or (not self.white_turn and piece_at_destination[0] == 'w')):  
                        every_possible_moves.append(Move((row, col), (end_row, end_col), self.board))
                        break  # Stop further moves in this direction
                    # Friendly piece
                    else:  
                        break  # Stop further moves in this direction
                else:
                    break  # Out of bounds

    # K n I G H T   M O V E S   Generator
    def kNight_moves_generator(self, row, col, every_possible_moves):
        
        #                2up-1L/R           1up-2L/R     2down-1L/R      1down-2L/R
        directions = ((-2,-1), (-2,1), (-1,-2), (-1,2), (2,-1), (2,1), (1,-2), (1,2))
        
        for d in directions:

            end_row = row + d[0]
            end_col = col + d[1]

            if(0 <= end_row < ROWS and 0 <= end_col < COLUMNS):
                piece_at_destination = self.board[end_row][end_col]

                if (piece_at_destination == '--' or (self.white_turn and piece_at_destination[0] == 'b') or (not self.white_turn and piece_at_destination[0] == 'w') ):
                    every_possible_moves.append(Move((row, col), (end_row, end_col), self.board))

    # B I S H O P   M O V E S   Generator
    def bishop_moves_generator(self, row, col, every_possible_moves):

        # Up-Left, Up-Right, Down-Left, Down-Right
        direction = ((-1,-1), (-1,1), (1,-1), (1,1))
        
        # Same as rook
        for d in direction:

            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if(0 <= end_row < ROWS and 0 <= end_col < COLUMNS):
                    piece_at_destination = self.board[end_row][end_col]
                    
                    if piece_at_destination == '--': 
                        every_possible_moves.append(Move((row, col), (end_row, end_col), self.board))
                    
                    elif ((self.white_turn and piece_at_destination[0] == 'b') or (not self.white_turn and piece_at_destination[0] == 'w')):  
                        every_possible_moves.append(Move((row, col), (end_row, end_col), self.board))
                        break  
                    
                    else:  
                        break  
                else:
                    break  

    # Q U E E N   M O V E S   Generator
    def queen_moves_generator(self, row, col, every_possible_moves):
        
        # All the 8 directions
        # direction = ((-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,-1), (-1,1), (1,1))

        # These moves are of bishop and rook

        self.rook_moves_generator(row, col, every_possible_moves)
        self.bishop_moves_generator(row, col, every_possible_moves)

    # K I N G   M O V E S   Generator
    def king_moves_generator(self, row, col, every_possible_moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        friend = 'w' if self.white_turn else 'b'

        for d in directions:
            end_row = row + d[0]
            end_col = col + d[1]

            # Check if the move is within the board
            if 0 <= end_row < ROWS and 0 <= end_col < COLUMNS:
                piece_at_destination = self.board[end_row][end_col]

                # Allow the king to move to empty squares or capture enemy pieces
                if piece_at_destination == '--' or piece_at_destination[0] != friend:
                    every_possible_moves.append(Move((row, col), (end_row, end_col), self.board))


# Moves samalo bhaiyo
# It's Advance Python Time babyyy
@dataclass
class Move:
    row1: int
    col1: int
    row2: int
    col2: int
    move_ID: int
    piece_moved: str
    piece_captured: str
    pawn_promotion: bool
    is_enpassant_move: bool

    def __init__(self, initial_square, final_square, board, is_enpassant_move = False):
        self.row1 = initial_square[0]
        self.col1 = initial_square[1]
        self.row2 = final_square[0]
        self.col2 = final_square[1]
        self.move_ID = self.row1 * 1000 + self.col1 * 100 + self.row2 * 10 + self.col2
        self.piece_moved = board[self.row1][self.col1]
        self.piece_captured = board[self.row2][self.col2]
        self.pawn_promotion = False                         # For pawn promotion to queen

        if(self.piece_moved == 'wP' and self.row2 == 0) or (self.piece_moved == 'bP' and self.row2 == 7):
            self.pawn_promotion = True

        self.is_enpassant_move = is_enpassant_move

    # def __init__(self, initial_square, final_square, board):
    #     self.row1 = initial_square[0]
    #     self.col1 = initial_square[1]

    #     self.row2 = final_square[0]
    #     self.col2 = final_square[1]

    #     self.piece_moved = board[self.row1][self.col1]
    #     self.piece_captured = board[self.row2][self.col2]

    def get_chess_notation(self):
        return self.get_rank_file(self.row1, self.col1) + self.get_rank_file(self.row2, self.col2)

    def get_rank_file(self, row, col):
        # Convert board coordinates (row, col) to chess notation (e.g., (0, 0) -> 'a8')
        file = chr(97 + col)
        rank = str(8 - row)
        return file + rank        



# U S E R   I N T E R F A C E


# S Q U A R E S

class Square:

    def __init__(self, row, column, piece = None):
        self.row = row
        self.column = column
        self.piece = piece

# Function to load all the images
def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]

    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(f"images/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))

# Drawing the Chess board
def draw_board_and_pieces(screen, board):
    # Choosing if the correct color of square, whether it is light or dark
    for row in range(ROWS):
        for col in range(COLUMNS):
            if((row + col) % 2 == 0):           # The first square should be light and so the squares with co-ordinates whose sum is even
                color = (152, 255, 152)
            else:                               # The dark ones
                color = (34, 139, 34)
            
            # The drawing of squares
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            # Drawing of the pieces
            square = board[row][col]            # choosing the square on which we draw pieces

            if(square != '--'):                 # If square is not vacant in the original numpy gameboard
                screen.blit(IMAGES[square], pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))



            
# P Y G A M E    E S S E N T I A L

pygame.init()

# Screen Setting
screen = pygame.display.set_mode((HEIGHT, WIDTH))
clock = pygame.time.Clock()
screen.fill(pygame.Color("white"))
pygame.display.set_caption("Chess")

# Pieces are loaded in baby 
load_images()



    




# M A I N   G A M E   L O O P

running = True
game_state = Game_State()
valid_moves_list = game_state.valid_moves_generator()   # List for all valid moves
print(valid_moves_list)
print()
move_hasbeen_made = False                               # The flag variable so my cpu doesn't get fucked
selected_square = None            # Tuple having row and col of the selected square
all_selected_squares = []       # List consisting of two tuples of above type

while running:
    for event in pygame.event.get():

        if(event.type == pygame.QUIT):
            running = False
            pygame.quit()

#                                               SELECTION AND MOVING

        elif(event.type == pygame.MOUSEBUTTONDOWN):
            co_ordinates = pygame.mouse.get_pos()
            row = co_ordinates[1] // SQUARE_SIZE
            col = co_ordinates[0] // SQUARE_SIZE

            current_square = (row, col)

            # Player clicked the same square twice
            if(current_square in all_selected_squares):
                # Deselect the square
                all_selected_squares.remove(current_square)
                selected_square = None if not all_selected_squares else all_selected_squares[-1]
            else:
                # Selecting the square
                selected_square = current_square
                all_selected_squares.append(selected_square)
            
            if(len(all_selected_squares) == 2):
                # pass
                move = Move(all_selected_squares[0], all_selected_squares[1], game_state.board)
                print(move.get_chess_notation())

                for i in range(len(valid_moves_list)):
                    if(move == valid_moves_list[i]):
                        game_state.move_piece(valid_moves_list[i])
                        move_hasbeen_made = True
                        # reset
                        selected_square = None
                        all_selected_squares = []
                
                if not move_hasbeen_made:
                    all_selected_squares = [selected_square]

        elif(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_z):
                game_state.undo()
                move_hasbeen_made = True

    if(move_hasbeen_made):
        move_hasbeen_made = False
        valid_moves_list = game_state.valid_moves_generator()
        print(valid_moves_list)
        print()

    draw_board_and_pieces(screen, game_state.board)

    clock.tick(MAX_FPS)
    pygame.display.update()
    pygame.display.flip()



