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
        self.pins = []                      # Any piece that is pinned
        self.checks = []                    # Any piece responsible for check

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
        # # Step 1 -> Generate all the moves for myself
        # moves = self.all_moves_generator()

        # # Step 2 -> Taking one move at a time
        # for move in moves:
        #     self.move_piece(move)

        #     enemy_moves = self.all_moves_generator()

        valid_moves = []            # Not starightaway getting all the moves
        self.king_in_check, self.pins, self.checks = self.pins_and_check_generator()

        if self.white_turn:
            king_row = self.white_king_coordinates[0]
            king_col = self.white_king_coordinates[1]
        else:
            king_row = self.black_king_coordinates[0]
            king_col = self.black_king_coordinates[1]

        if(self.king_in_check):

            # 1. Only 1 Check is there on king
            # 2. Double Check is there on king

            # 1.
            # ---> a. Block     b. Get king out of way
            if(len(self.checks) == 1):
                valid_moves = self.all_moves_generator()

                # The particular check details (square information) containing tuple is selected
                check = self.checks[0]

                # Detailed analisis
                check_row = check[0]
                check_col = check[1]

                # Enemy piece causing the check
                enenmy_piece = self.board[check_row][check_col]

                # Squares that piece can move to prevent check
                valid_squares = []

                # Knight is here..!!
                # Cooked ->
                # 1. Move the king
                # 2. Capture Knight
                if(enenmy_piece[1] == 'N'):
                    valid_squares = [(check_row, check_col)]        # Capturing the kinght

                # Relif -> 
                # Block the check
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        # We got to the piece, no more squares to play with, break
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                
                # Removing the not possible moves
                # Iterating backwards are we are removing something and i dont want shifting to get in beef with me
                # for i in range(len(valid_moves) - 1, -1, -1):
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
                #     # if king is not moved... then the move must be capturing the enemy or atleast blocking it
                #     if(valid_moves[i].piece_moved[1] != 'K'):

                #         # Removing moves that does nothing
                #         if not (valid_moves[i].row2, valid_moves[i].col2) in valid_squares:
                #             valid_moves.remove(valid_moves[i])

                # Create a new list with valid moves (instead of modifying the list during iteration)
                valid_moves = [
                    move for move in valid_moves
                    if move.piece_moved[1] == 'K' or (move.row2, move.col2) in valid_squares
                ]

            
            # 2.
            # Double check condition
            # King has to move so all valid moves are kings move 
            else:
                self.king_moves_generator(king_row, king_col, valid_moves)

        # No checks 
        else:
            valid_moves = self.all_moves_generator()

        return valid_moves

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

        return every_possible_moves

    # P A W N   M O V E S   Generator
    def pawn_moves_generator(self, row, col, every_possible_moves):
        piece_pinning = False
        pin_direction = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinning = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if(self.white_turn): # White turn

            # One square forward
            if(self.board[row-1][col] == '--'):
                if not piece_pinning or pin_direction == (-1, 0):
                    every_possible_moves.append(Move((row, col), (row-1, col), self.board))
                    # Two square forward.. A one time case
                    if(row == 6 and self.board[row-2][col] == '--'):  # We are using nested if because the two square advance move will be from the same start square
                        every_possible_moves.append(Move((row, col), (row-2, col), self.board))
            
            # Capture

            # left diagonal direction
            if(col - 1 >= 0):
                if(self.board[row-1][col-1][0] == 'b'):     # Enenmy
                    if not piece_pinning or pin_direction == (-1, -1):
                        every_possible_moves.append(Move((row, col), (row-1, col-1), self.board))
            # right diagonal direction
            if(col + 1 < COLUMNS):
                if(self.board[row-1][col+1][0] == 'b'):
                    if not piece_pinning or pin_direction == (-1, 1):
                        every_possible_moves.append(Move((row, col), (row-1, col+1), self.board))

        else:   # Black Turn
            if(self.board[row+1][col] == '--'):
                if not piece_pinning or pin_direction == (1, 0):
                    every_possible_moves.append(Move((row, col), (row+1, col), self.board))

                    if(row == 1 and self.board[row+2][col] == '--'):  
                        every_possible_moves.append(Move((row, col), (row+2, col), self.board))
            
            if(col - 1 >= 0):
                if(self.board[row+1][col-1][0] == 'w'):  
                    if not piece_pinning or pin_direction == (1, -1):   
                        every_possible_moves.append(Move((row, col), (row+1, col-1), self.board))
                
            if(col + 1 < COLUMNS):
                if(self.board[row+1][col+1][0] == 'w'):
                    if not piece_pinning or pin_direction == (1, 1): 
                        every_possible_moves.append(Move((row, col), (row+1, col+1), self.board))

        #         direction = -1 if self.white_turn else 1  # White moves up (-1), Black moves down (+1)
        # start_row = 6 if self.white_turn else 1
        # enemy = 'b' if self.white_turn else 'w'

        # # One square forward
        # if self.board[row + direction][col] == '--':
        #     every_possible_moves.append(Move((row, col), (row + direction, col), self.board))
        #     # Two squares forward
        #     if row == start_row and self.board[row + 2*direction][col] == '--':
        #         every_possible_moves.append(Move((row, col), (row + 2*direction, col), self.board))

        # # Captures
        # for offset in [-1, 1]:  # Diagonal left and right
        #     if 0 <= col + offset <= 7:
        #         if self.board[row + direction][col + offset][0] == enemy:
        #             every_possible_moves.append(Move((row, col), (row + direction, col + offset), self.board))

    # R O O K   M O V E S   Generator
    def rook_moves_generator(self, row, col, every_possible_moves):
        piece_pinning = False
        pin_direction = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinning = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if(self.board[row][col][1] != 'Q'):
                    self.pins.remove(self.pins[i])
                break

        # Up, Down, Left, Right
        direction = ((-1,0), (1,0), (0,-1), (0,1))

        for d in direction:

            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                # Check for boundation
                if(0 <= end_row < ROWS and 0 <= end_col < COLUMNS):
                    if not piece_pinning or pin_direction == d or pin_direction == (-d[0], -d[1]):
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

        piece_pinning = False

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinning = True
                self.pins.remove(self.pins[i])
                break

        
        #                2up-1L/R           1up-2L/R     2down-1L/R      1down-2L/R
        directions = ((-2,-1), (-2,1), (-1,-2), (-1,2), (2,-1), (2,1), (1,-2), (1,2))
        
        for d in directions:

            end_row = row + d[0]
            end_col = col + d[1]

            if(0 <= end_row < ROWS and 0 <= end_col < COLUMNS):

                if not piece_pinning:
                    piece_at_destination = self.board[end_row][end_col]

                    if (piece_at_destination == '--' or (self.white_turn and piece_at_destination[0] == 'b') or (not self.white_turn and piece_at_destination[0] == 'w') ):
                        every_possible_moves.append(Move((row, col), (end_row, end_col), self.board))

    # B I S H O P   M O V E S   Generator
    def bishop_moves_generator(self, row, col, every_possible_moves):

        piece_pinning = False
        pin_direction = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinning = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break


        # Up-Left, Up-Right, Down-Left, Down-Right
        direction = ((-1,-1), (-1,1), (1,-1), (1,1))
        
        # Same as rook
        for d in direction:

            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if(0 <= end_row < ROWS and 0 <= end_col < COLUMNS):
                    if not piece_pinning or pin_direction == d or pin_direction == (-d[0], -d[1]):
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
        # row_moves = (-1,-1,-1,0,0,1,1,1)
        # col_moves = (-1,0,1,-1,1,-1,0,1)
        # friend = 'w' if self.white_turn else 'b'

        # for i in range(1, 8):
        #     end_row = row + row_moves[i]
        #     end_col = col + col_moves[i]
        #     if 0 <= end_row < ROWS and 0 <= end_col < COLUMNS:
        #         piece_at_destination = self.board[end_row][end_col]

        #         # Check if the square is empty or occupied by an enemy piece
        #         if(piece_at_destination != friend):
        #             # check for check on final square and check for checks
        #             if(friend == 'w'):
        #                 self.white_king_coordinates = (end_row, end_col)
        #             else:
        #                 self.black_king_coordinates = (end_row, end_col)

        #             king_in_check, pins, checks = self.pins_and_check_generator()

        #             if not king_in_check:
        #                 every_possible_moves.append(Move((row, col), (end_row, end_col), self.board))

        #             # Reset the king back to original
        #             if(friend == 'w'):
        #                 self.white_king_coordinates = (row, col)
        #             else:
        #                 self.white_king_coordinates = (row, col)

        # Up, Down, Left, Right, and Diagonals
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d in directions:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < ROWS and 0 <= end_col < COLUMNS:
                piece_at_destination = self.board[end_row][end_col]
                # Check if the square is empty or occupied by an enemy piece
                if piece_at_destination == '--' or (self.white_turn and piece_at_destination[0] == 'b') or (not self.white_turn and piece_at_destination[0] == 'w'):

                    # check for check on final square and check for checks
                    if(self.white_turn):
                        self.white_king_coordinates = (end_row, end_col)
                    else:
                        self.black_king_coordinates = (end_row, end_col)

                    king_in_check, pins, checks = self.pins_and_check_generator()

                    if not(king_in_check):
                        every_possible_moves.append(Move((row, col), (end_row, end_col), self.board))

                    # Reset the king back to original
                    if(self.white_turn):
                        self.white_king_coordinates = (row, col)
                    else:
                        self.white_king_coordinates = (row, col)

    def pins_and_check_generator(self):
        # Squares where the allied pinned piece is and direction pinned from
        pins = []

        # Squares where enemy is applying a check 
        checks = []

        # Check on King
        king_in_check = False

        if self.white_turn:
            friend = 'w'
            enemy = 'b'
            start_row = self.white_king_coordinates[0]
            start_col = self.white_king_coordinates[1]
        else:
            friend = 'b'
            enemy = 'w'
            start_row = self.black_king_coordinates[0]
            start_col = self.black_king_coordinates[1]

        # Directions out of the king in all 8 directions
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

        # Check all the 8 directions
        for j in range(len(directions)):

            d = directions[j]

            possible_pin = ()                       # Reseting the tuple

            # Check in all the maximum 7 squares
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i

                if(0 <= end_row < ROWS and 0 <= end_col < COLUMNS):

                    piece_at_destination = self.board[end_row][end_col]

                    # Nice, we got a protector
                    if(piece_at_destination[0] == friend and piece_at_destination[1] != 'K'):

                        # First friend, can be a pin
                        if(possible_pin == ()):
                            possible_pin = (end_row, end_col, d[0], d[1])
                        # Second piece in same direction, so our king is safe in this direction, i.e. no pin or check possible in this direction
                        else:
                            break
                    
                    # Ah Shit!
                    elif(piece_at_destination[0] == enemy):

                        piece_name = piece_at_destination[1]

                        # 1. Queen -> Any fuking direction
                        # 2. Rook -> Up, Down, Left, Right
                        # 3. Bishop -> Diagonal bitch
                        # 4. Knight -> dhai chal => Multidirectional OP bitch   ==>> TAKEN CARE SEPARATELY
                        # 5. Pawn -> Diagonal WEAK bitch => One Square threat => Only Up (w) or Only Down(b)
                        # 6. King -> Any direction => One square threat

                        if( (piece_name == 'Q') or (piece_name == 'R' and 0 <= j <= 3) or (piece_name == 'B' and 4 <= j <= 7) or (i == 1 and piece_name == 'P' and ((enemy == 'w' and 6 <= j <= 7) or (enemy == 'b' and 4 <= j <= 5)))  or (piece_name == 'K' and i == 1) ):
                            
                            # No cover
                            if(possible_pin == ()):
                                king_in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            # Less go geting my friend in my enemy's way 
                            else:
                                pins.append((end_row, end_col, d[0], d[1]))
                                break
                        
                        # Enemy piece is useless
                        else:
                            break
                # Off the board 
                else:
                    break

        # Kingth is here bitch
        # No condition for pin as this mf jumps over the pieces
        directions_for_knight = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1 ,2), (2, -1), (2, 1))

        for d in directions_for_knight:
            end_row = start_row + d[0]
            end_col = start_col + d[1]

            if(0 <= end_row < ROWS and 0 <= end_col < COLUMNS):

                    piece_at_destination = self.board[end_row][end_col]

                    # King is cooked
                    if(piece_at_destination[0] == enemy and piece_at_destination[1] == 'N'):
                        king_in_check = True
                        checks.append((end_row, end_col, d[0], d[1]))

        return king_in_check, pins, checks




# Moves samalo bhaiyo
# It's Advance Python Time babyyy
@dataclass
class Move:
    row1: int
    col1: int
    row2: int
    col2: int
    piece_moved: str
    piece_captured: str

    def __init__(self, initial_square, final_square, board):
        self.row1 = initial_square[0]
        self.col1 = initial_square[1]
        self.row2 = final_square[0]
        self.col2 = final_square[1]
        self.piece_moved = board[self.row1][self.col1]
        self.piece_captured = board[self.row2][self.col2]

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

                if(move in valid_moves_list):
                    game_state.move_piece(move)
                    move_hasbeen_made = True
                    # reset
                    selected_square = None
                    all_selected_squares = []
                else:
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



