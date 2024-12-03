#S.A.M -> Systematic Advanced Machine
import random
import numpy as np

piece_power = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'P': 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

counter_pruning = 0



def random_move_generator(valid_moves):
    if not valid_moves:
        return None
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


# def best_move_generator(game_state, valid_moves):
#     if not valid_moves:
#         return None

#     turn_type = 1 if game_state.white_turn else -1
#     opponent_min_max_score = CHECKMATE
#     best_player_move = None

#     random.shuffle(valid_moves)

#     for player_move in valid_moves:
#         game_state.move_piece(player_move)

#         opponent_moves = game_state.valid_moves_generator()

#         if(game_state.check_mate):
#             opponent_max_score = -CHECKMATE
#         elif(game_state.stale_mate):
#             opponent_max_score = STALEMATE
#         else:
#             opponent_max_score = -CHECKMATE
#             for opponent_move in opponent_moves:
#                 game_state.move_piece(opponent_move)
#                 game_state.valid_moves_generator()
#                 if game_state.check_mate:
#                     score = -CHECKMATE * -turn_type
#                 elif game_state.stale_mate:
#                     score = STALEMATE
#                 else:
#                     score = -turn_type * score_material(game_state.board)

#                 if score > opponent_max_score:
#                     opponent_max_score = score

#                 game_state.undo()

#         if opponent_max_score < opponent_min_max_score:
#             opponent_min_max_score = opponent_max_score
#             best_player_move = player_move

#         game_state.undo()

#     return best_player_move




# White -> Positive -> Good 
# Black -> Negative -> Good

def best_move_generator(game_state, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    # counter_pruning = 0
    next_move_alpha_beta_pruning(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.white_turn else -1)


    print(f"Pruning: {counter_pruning}")
    # print(f"MiniMax: {counter_neg}")

# Mini-Max algorithim
def next_move_alpha_beta_pruning(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter_pruning

    # counter_pruning += 1
    # print(counter_pruning)

    if(depth == 0):
        return turn_multiplier * score_material(game_state)

    max_score = -CHECKMATE

    for move in valid_moves:

        game_state.move_piece(move)

        next_valid_moves = game_state.valid_moves_generator()

        score = -next_move_alpha_beta_pruning(game_state, next_valid_moves, depth - 1, -beta, -alpha, -turn_multiplier)     # not white_turn

        if(score > max_score):
            max_score = score
            if(depth == DEPTH):
                next_move = move

        game_state.undo()

        if(max_score > alpha):
            alpha = max_score

        if(alpha >= beta):
            break


    return max_score




# def score_material(game_state):
#     if game_state.check_mate:  # Ensure this accesses the correct object
#         if game_state.white_turn:
#             return -CHECKMATE
#         else:
#             return CHECKMATE
#     elif game_state.stale_mate:
#         return STALEMATE

#     score = 0
#     for row in game_state.board:
#         for square in row:
#             if square:
#                 if square[0] == 'w':
#                     score += piece_power[square[1]]
#                 elif square[0] == 'b':
#                     score -= piece_power[square[1]]
#     return score

def score_material(game_state):
    if game_state.check_mate:
        return -CHECKMATE if game_state.white_turn else CHECKMATE
    elif game_state.stale_mate:
        return STALEMATE

    # Convert the board to a NumPy array if it's not already
    board = game_state.board

    # Define NumPy arrays for piece power and identifiers
    piece_power = np.array([0, 1, 3, 3, 5, 10])  # Corresponding to ['K', 'P', 'N', 'B', 'R', 'Q']
    piece_map = {'.': 0, ' ': 0, 'K': 0, 'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5}

    # Flatten the board and parse it into piece types and colors
    pieces = np.chararray.flatten(board)  # Flatten the board
    white_mask = np.char.startswith(pieces, 'w')  # Boolean mask for white pieces
    black_mask = np.char.startswith(pieces, 'b')  # Boolean mask for black pieces

    # Strip colors to get piece types only
    stripped_pieces = np.char.strip(pieces, 'wb')

    # Convert piece types to indices using the piece_map
    piece_indices = np.vectorize(lambda x: piece_map.get(x, 0))(stripped_pieces.astype(str))

    # Calculate scores for white and black
    white_score = np.sum(piece_power[piece_indices][white_mask])
    black_score = np.sum(piece_power[piece_indices][black_mask])

    return white_score - black_score




# def score_material(board):
    
#     score = 0
#     for row in board:
#         for square in row:
#             if square:
#                 if square[0] == 'w':
#                     score += piece_power[square[1]]
#                 elif square[0] == 'b':
#                     score -= piece_power[square[1]]
#     return score

