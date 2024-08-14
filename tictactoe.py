"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    game_over = "The game is already over"

    o_moves = []
    x_moves = []
    if terminal(board):
        return game_over
    elif board == initial_state():
        x_moves.append(X)
        return X
    else:
        for i in range(3):
            for j in range(3):
                if board[i][j] == X:
                    x_moves.append(X)
                elif board[i][j] == O:
                    o_moves.append(O)

        if len(x_moves) > len(o_moves):
            return O
        elif len(x_moves) == len(o_moves):
            return X

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    game_over = "The game is already over"
    action = set()
    if terminal(board):
        return game_over
    else:
        for i in range(3):
            for j in range(3):
                if board[i][j] == EMPTY:
                    action.add((i, j))

    return action

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i = action[0]
    j = action[1]
    board_copy = copy.deepcopy(board)

    if board[i][j] == EMPTY:
        board_copy[i][j] = player(board_copy)
        return board_copy
    else:
        raise Exception("Invalid action!")

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    if horizontal_win_check(board) == X:
        return X
    elif horizontal_win_check(board) == O:
        return O

    if vertical_win_check(board) == X:
        return X
    elif vertical_win_check(board) == O:
        return O

    if diagonal_win_check(board) == X:
        return X
    elif diagonal_win_check(board) == O:
        return O

    else:
        return EMPTY

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    list_empty = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                list_empty.append(EMPTY)

    if winner(board) == X:
        return True
    elif winner(board) == O:
        return True
    elif len(list_empty) == 0:
        return True
    else:
        return False

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    opt_action = ()
    if terminal(board):
        return EMPTY
    else:
        if player(board) == X:
            v = -math.inf
            for action in actions(board):
                t = min_value(result(board, action))
                if t == 1:
                    opt_action = action
                if t > v:
                    v = t
                    opt_action = action

        else:
            v = math.inf
            for action in actions(board):
                t = max_value(result(board, action))
                if t == -1:
                    opt_action = action
                if t < v:
                    v = t
                    opt_action = action

    return opt_action

def max_value(board):
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v

def horizontal_win_check(board):
    if board[0][0] == board[0][1] == board[0][2] == X:
        return X
    elif board[0][0] == board[0][1] == board[0][2] == O:
        return O

    if board[1][0] == board[1][1] == board[1][2] == X:
        return X
    elif board[1][0] == board[1][1] == board[1][2] == O:
        return O

    if board[2][0] == board[2][1] == board[2][2] == X:
        return X
    elif board[2][0] == board[2][1] == board[2][2] == O:
        return O

def vertical_win_check(board):
    if board[0][0] == board[1][0] == board[2][0] == X:
        return X
    elif board[0][0] == board[1][0] == board[2][0] == O:
        return O

    if board[0][1] == board[1][1] == board[2][1] == X:
        return X
    elif board[0][1] == board[1][1] == board[2][1] == O:
        return O

    if board[0][2] == board[1][2] == board[2][2] == X:
        return X
    elif board[0][2] == board[1][2] == board[2][2] == O:
        return O

def diagonal_win_check(board):
    if board[0][0] == board[1][1] == board[2][2] == X:
        return X
    elif board[0][0] == board[1][1] == board[2][2] == O:
        return O

    if board[0][2] == board[1][1] == board[2][0] == X:
        return X
    elif board[0][2] == board[1][1] == board[2][0] == O:
        return O



