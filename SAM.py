#S.A.M -> Systematic Advanced Machine
import random

piece_power = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'P': 1}
CHECKMATE = 1000
STALEMATE = 0


def random_move_generator(valid_moves):
    if not valid_moves:
        return None
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def best_move_generator(game_state, valid_moves):
    if not valid_moves:
        return None

    turn_type = 1 if game_state.white_turn else -1
    opponent_min_max_score = CHECKMATE
    best_player_move = None

    random.shuffle(valid_moves)

    for player_move in valid_moves:
        game_state.move_piece(player_move)

        opponent_moves = game_state.valid_moves_generator()
        if not opponent_moves:  # No opponent moves
            if game_state.check_mate:
                opponent_max_score = -CHECKMATE
            elif game_state.stale_mate:
                opponent_max_score = STALEMATE
            else:
                opponent_max_score = turn_type * score_material(game_state.board)
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponent_moves:
                game_state.move_piece(opponent_move)

                if game_state.check_mate:
                    score = -CHECKMATE * -turn_type
                elif game_state.stale_mate:
                    score = STALEMATE
                else:
                    score = -turn_type * score_material(game_state.board)

                if score > opponent_max_score:
                    opponent_max_score = score

                game_state.undo()

        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move

        game_state.undo()

    return best_player_move


def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square:
                if square[0] == 'w':
                    score += piece_power[square[1]]
                elif square[0] == 'b':
                    score -= piece_power[square[1]]
    return score
