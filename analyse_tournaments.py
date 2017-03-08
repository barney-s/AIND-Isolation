"""
Utility to analyse game runs
"""

import os
import pickle
import pandas

def load_runs():
    """ return the loaded games one by one
    """
    i = 0
    while os.path.exists("run%s.dat" % i):
        games = pickle.load(open("run%s.dat"%i, "rb"))
        i += 1
        for _game in games:
            yield _game

open_book = {}
MOVE_DEPTH=3
move_score = [[[0 for x in range(7)] for y in range(7)] for d in range(MOVE_DEPTH)]

def analyse_game(game):
    """analyse game run
    """
    if "Student" in [game["p1"], game["p2"]]:
        idx = 0 if game["p1"] == "Student" else 1
        won = game["winner"] == "Student"
        moves = []
        for i in range(MOVE_DEPTH):
            try:
                moves.append(game["moves"][i][idx])
            except IndexError:
                moves = []
                break
        if not open_book.get(tuple(moves)): 
            open_book[tuple(moves)] = { "won": 0, "lost": 0 }
        idx = 0
        for move in moves:
           move_score[idx][moves[idx][0]][moves[idx][1]] += 1 if won else -1
           idx += 1
        open_book[tuple(moves)]["won" if won else "lost"] += 1

def to_string(matrix):
    """Generate a string representation of the current game state, marking
    the location of each player and indicating which cells have been
    blocked, and which remain open.
    """
    out = ''
    width = len(matrix)
    height = len(matrix[0])
    for i in range(height):
        out += ' | '
        for j in range(width):
            out += "%2d"%(matrix[i][j])
            out += ' | '
        out += '\n\r'
    return out

if __name__ == "__main__":
    for run in load_runs():
        analyse_game(run)
    #ob = pandas.DataFrame.from_dict(open_book)
    for idx in range(MOVE_DEPTH):
        print("%d move score:\n%s"%(idx + 1, to_string(move_score[idx])))
    pickle.dump(move_score, open("move_score.dat", "wb"))
