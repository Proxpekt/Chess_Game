#S.A.M -> Systematic Advanced Machine
import random

piece_power = {'K':0, 'Q': 10, 'R':5, 'B': 3, 'N': 3, 'P': 1}
CHECKMATE = 1000
STALEMATE = 0


def random_move_generator(valid_moves):

    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def best_move_generator(game_state, valid_moves):
    turn_type = 1 if game_state.white_turn else -1
    max_score = -CHECKMATE
    best_move = None

    for player_move in valid_moves:
        game_state.move_piece(player_move)
        
        if(game_state.check_mate):
            score = CHECKMATE
        elif(game_state.stale_mate):
            score = STALEMATE
        else:
            score = turn_type * score_material(game_state.board)

        if(score > max_score):
            max_score = score
            best_move = player_move

        game_state.undo()

    return best_move




def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if(square[0] == 'w'):
                score += piece_power[square[1]]
            elif(square[0] == 'b'):
                score -= piece_power[square[1]]

    return score