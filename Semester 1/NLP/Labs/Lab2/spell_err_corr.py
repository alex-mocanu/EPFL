import numpy as np


# FSA implementation
class State:
    def __init__(self, id):
        self.id = id
        self._final = False
        self.next_states = {}

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return self.__str__()

    def add_transition(self, symbol, state):
        self.next_states[symbol] = state

    def make_final(self):
        self._final = True


class FSA:
    def __init__(self, alphabet):
        self.alphabet = alphabet
        self.init_state = State(0)
        self.states = [self.init_state]

    def insert(self, string):
        n = len(string)
        curr_state = self.init_state
        for i in range(n):
            next_state = curr_state.next_states.get(string[i])
            if next_state is not None:
                curr_state = next_state
            else:
                new_state = State(len(self.states))
                curr_state.add_transition(string[i], new_state)
                self.states.append(new_state)
                curr_state = new_state
        # Make the last state final
        curr_state.make_final()

    def next_state(self, state, symbol):
        return self.states[state].next_state[symbol]


# Solving the task at hand
def edit_distance(X, Y):
    n, m = len(X), len(Y)
    chart = np.zeros([n + 1, m + 1])

    # Initialize first row and first column
    chart[:, 0] = range(n + 1)
    chart[0, :] = range(m + 1)

    # Fill the chart
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if X[i - 1] == Y[j - 1]:
                chart[i, j] = chart[i - 1, j - 1]
            elif i >= 2 and j >= 2 and X[i - 2] == Y[j - 1] and X[i - 1] == Y[j - 2]:
                chart[i, j] = 1 + min(chart[i - 2, j - 2], chart[i - 1, j], chart[i, j - 1])
            else:
                chart[i, j] = 1 + min(chart[i - 1, j - 1], chart[i - 1, j], chart[i, j - 1])

    return chart


def cutoff_dist(chart, X, Y, theta):
    n = len(X)
    m = len(Y)
    assert chart.shape[0] == n + 1 and chart.shape[1] >= m

    # Compute the new column
    new_column = np.zeros(n + 1)
    new_column[0] = m
    for i in range(1, n + 1):
        if X[i - 1] == Y[m - 1]:
            new_column[i] = chart[i - 1, m - 1]
        elif i >= 2 and m >= 2 and X[i - 2] == Y[m - 1] and X[i - 1] == Y[m - 2]:
            new_column[i] = 1 + min(chart[i - 2, m - 2], new_column[i - 1], chart[i, m - 1])
        else:
            new_column[i] = 1 + min(chart[i - 1, m - 1], new_column[i - 1], chart[i, m - 1])

    if chart.shape[1] == m:
        new_column = new_column.reshape(-1, 1)
        chart = np.append(chart, new_column, axis=1)
    else:
        chart[:, m] = new_column

    # Compute thresholds for searching for the cutoff distance
    I = min(n, max(1, m - theta))
    J = min(n, max(1, m + theta))
    last_col = chart[:, m]

    return np.min(last_col[I:J + 1]), chart


# Dummy hardcoded FSA
alphabet = ['a', 'b']

def next_state(state, symbol):
    if state == 1:
        if symbol == 'a':
            return 2
        elif symbol == 'b':
            return 4
    elif state == 2 and symbol == 'b':
        return 3
    elif state == 3 and symbol == 'a':
        return 1
    elif state == 4 and symbol == 'a':
        return 5
    elif state == 5 and symbol == 'b':
        return 1
    return None


def is_final(state):
    return state == 1


def make_correction(err_str, sol_str, state, chart, theta, solutions):
    for letter in alphabet:
        q = next_state(state, letter)
        if q is not None:
            Y = sol_str + letter
            cutoff, chart = cutoff_dist(chart, err_str, Y, theta)
            if cutoff <= theta:
                make_correction(err_str, Y, q, chart, theta, solutions)
                if is_final(q) and chart[len(err_str), len(Y)] <= theta:
                    solutions.append(Y)

    return solutions


if __name__ == '__main__':
    # Initialize edit distance chart
    chart = edit_distance('abba', '')
    solutions = []

    make_correction('abba', '', 1, chart, 2, solutions)
    print(solutions)
