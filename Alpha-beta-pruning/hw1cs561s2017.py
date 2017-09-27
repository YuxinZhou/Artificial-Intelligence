##################################################
# Global variable and utility functions
Infinity = float('inf')
Game_over = False
Start_player = 1
b_size = 8
depth = 0
cut_off = float('inf')
evaluation = [[99, -8, 8, 6, 6, 8, -8, 99],
              [-8, -24, -4, -3, -3, -4, -24, -8],
              [8, -4, 7, 4, 4, 7, -4, 8],
              [6, -3, 4, 0, 0, 4, -3, 6],
              [6, -3, 4, 0, 0, 4, -3, 6],
              [8, -4, 7, 4, 4, 7, -4, 8],
              [-8, -24, -4, -3, -3, -4, -24, -8],
              [99, -8, 8, 6, 6, 8, -8, 99]]
traces = ['Node,Depth,Value,Alpha,Beta']  # trace for searching tree
next_actions = {}  # all valid actions and its value


def deepcopy_2D_list(l):
    return [x[:] for x in l]


def value_str(x):
    if x == Infinity:
        return 'Infinity'
    elif x == -Infinity:
        return '-Infinity'
    else:
        return str(x)


##################################################


def main():
    global cut_off
    S = read_from_file('input.txt')
    alpha_beta_search(S)
    S = next_state(S)
    write_to_file('output.txt', S)


class State:
    def __init__(self, board, player):
        """
        :param board: current board
        :param player: current player to move, -1 or 1
        :type board: int[b_size][b_size]
        :type player: int
        """
        self.board = board
        self.player = player

    def is_valid_pos(self, i, j):
        if self.board[i][j] != 0:
            return False
        result = False
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, 1), (-1, -1), (1, 1), (1, -1)]
        for di, dj in directions:
            result = result or self.check_by_direction(i, j, di, dj)
        return result

    def check_by_direction(self, i, j, di, dj):
        i, j = i + di, j + dj
        if i >= b_size or i < 0 or j >= b_size or j < 0:
            return False
        if self.board[i][j] == self.player or self.board[i][j] == 0:
            return False
        i, j = i + di, j + dj
        while b_size > i >= 0 and b_size > j >= 0:
            if self.board[i][j] == self.player:
                return True
            if self.board[i][j] == 0:
                return False
            i, j = i + di, j + dj
        return False

    def update_board(self, i, j):
        self.board[i][j] = self.player
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, 1), (-1, -1), (1, 1), (1, -1)]
        for di, dj in directions:
            if self.check_by_direction(i, j, di, dj):
                self.update_by_direction(i, j, di, dj)
        return

    def update_by_direction(self, i, j, di, dj):
        i, j = i + di, j + dj
        while b_size > i >= 0 and b_size > j >= 0:
            if self.board[i][j] != self.player:
                self.board[i][j] = self.player
                i, j = i + di, j + dj
            else:
                return


def max_value(state, alpha, beta, now):
    """
    Recursive alpha-beta pruning function
    :param state: state after placing a piece at position 'now'
    :param alpha: alpha in a-b pruning
    :param beta: beta in a-b pruning
    :param now: last action taken
    :type state: State
    :type alpha: int
    :type beta: int
    :type now: (int, int)

    :return: value
    :rtype: int
    """
    global depth, Game_over
    acts = actions(state)
    if Game_over or depth >= cut_off:  # Terminal test
        v = utility(state)
        keep_trace(now, depth, v, alpha, beta)
        return v
    v = - Infinity
    keep_trace(now, depth, v, alpha, beta)
    if len(acts) == 0 and now == 'pass':
        acts.append('pass')
        Game_over = True
    elif len(acts) == 0 and now != 'pass':
        acts.append('pass')
    else:
        Game_over = False
    for a in acts:
        Game_over = False
        depth = depth + 1
        copy, player = deepcopy_2D_list(state.board), state.player
        v = max(v, min_value(take_action(state, a), alpha, beta, a))
        depth = depth - 1
        state.board, state.player = deepcopy_2D_list(copy), player
        if v >= beta:
            keep_trace(now, depth, v, alpha, beta)
            alpha = max(alpha, v)
            return v
        alpha = max(alpha, v)
        keep_trace(now, depth, v, alpha, beta)
    return v


def min_value(state, alpha, beta, now):
    """
    Recursive alpha-beta pruning function
    :param state: state after placing a piece at position 'now'
    :param alpha: alpha in a-b pruning
    :param beta: beta in a-b pruning
    :param now: last action taken
    :type state: State
    :type alpha: int
    :type beta: int
    :type now: (int, int)

    :return: value
    :rtype: int
    """
    global depth, Game_over
    acts = actions(state)
    if Game_over or depth >= cut_off:  # Terminal test
        v = utility(state)
        keep_trace(now, depth, v, alpha, beta)
        return v
    v = Infinity
    keep_trace(now, depth, v, alpha, beta)
    if len(acts) == 0 and now == 'pass':
        acts.append('pass')
        Game_over = True
    elif len(acts) == 0 and now != 'pass':
        acts.append('pass')
    else:
        Game_over = False
    for a in acts:
        depth = depth + 1
        copy, player = deepcopy_2D_list(state.board), state.player
        v = min(v, max_value(take_action(state, a), alpha, beta, a))
        depth = depth - 1
        state.board, state.player = deepcopy_2D_list(copy), player
        if v <= alpha:
            keep_trace(now, depth, v, alpha, beta)
            beta = min(beta, v)
            return v
        beta = min(beta, v)
        keep_trace(now, depth, v, alpha, beta)
    return v


def alpha_beta_search(state):
    """
    Initial call
    :param state: initial state
    :type state: State

    :return: value
    :rtype: int
    """
    v = max_value(state, -Infinity, Infinity, 'root')
    return v


def utility(state):
    """
    Calculate the value of a terminal state
    :param state: terminal state
    :return: value

    :type state: State
    :rtype: int
    """
    board = state.board
    result = 0
    for i in range(b_size):
        for j in range(b_size):
            result = result + board[i][j] * evaluation[i][j]
    return result if Start_player == 1 else -result


def actions(state):
    """
    Return all valid moves available to State.player on current state.board
    :param state: current state
    :type state: State

    :return: all valid moves
    :rtype: List[(int,int)]
    """
    result = []
    for i in range(b_size):
        for j in range(b_size):
            if state.is_valid_pos(i, j):
                result.append((i, j))
    return result


def take_action(state, a):
    """
    Return new state after placing a piece at position 'a' on current state.board
    :param state: current state
    :type state: State
    :param a: action
    :type a: (int,int)

    :return: new state
    :rtype: State
    """
    if a != 'pass':
        i, j = a
        state.update_board(i, j)
    state.player = - state.player
    return state


def keep_trace(a, depth, v, alpha, beta):
    trace = []
    if a == 'root':
        trace.append('root')
    elif a == 'pass':
        trace.append('pass')
    else:
        i, j = a
        column = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
        trace.append('{0}{1}'.format(column[j], i + 1))
    trace.append(value_str(depth))
    trace.append(value_str(v))
    trace.append(value_str(alpha))
    trace.append(value_str(beta))
    traces.append(','.join(trace))
    if depth == 1 and a != 'pass':
        next_actions[a] = v
    return


def next_state(state):
    l = []  # to sort the next state
    for key, value in next_actions.iteritems():
        l.append((value, key))
    l.sort(key=lambda x: x[1])  # rank by value in descending order
    l.sort(key=lambda x: x[0], reverse=True)  # rank by position in ascending order
    if len(l) == 0:
        return state
    i, j = l[0][1]
    state.update_board(i, j)
    return state


def read_from_file(fname):
    global cut_off, Start_player
    f = open(fname, 'r')
    player = f.readline()[0]
    if player == 'X':
        Start_player = 1
    elif player == 'O':
        Start_player = -1
    cut_off = int(f.readline())
    board = f.readlines(8)
    b = [[0 for col in range(b_size)] for row in range(b_size)]
    for i in range(b_size):
        for j in range(b_size):
            if board[i][j] == '*':
                b[i][j] = 0
            elif board[i][j] == 'O':
                b[i][j] = -1
            elif board[i][j] == 'X':
                b[i][j] = 1
    f.close()
    state = State(b, Start_player)
    return state


def write_to_file(fname, state):
    f = open(fname, 'w')
    dict = {0: '*', 1: 'X', -1: 'O'}
    b = [[0 for col in range(b_size)] for row in range(b_size)]  # board to print
    for i in range(b_size):
        for j in range(b_size):
            b[i][j] = dict[state.board[i][j]]
    for i in b:  # print board
        f.write(''.join(i))
        f.write('\n')
    f.write('\n'.join(traces))  # print traces
    f.close()


if __name__ == '__main__':
    main()
