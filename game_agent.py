"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
#from random import randint
import logging
import sys
import math
import os
import pickle

LOG = logging.getLogger()
LOG.level = logging.DEBUG #ERROR < INFO < DEBUG
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
LOG.addHandler(STREAM_HANDLER)

search_depth = []

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


#move_score = pickle.load(open("move_score.dat", "rb"))

def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        #LOG.info("%s LOST", player.__class__)
        return float("-inf")

    if game.is_winner(player):
        #LOG.info("%s WON", player.__class__)
        return float("inf")

    my_pos = game.get_player_location(player)
    op_pos = game.get_player_location(game.get_opponent(player))
    center = (game.width/2, game.height/2)

    #LOG.debug("\ngetting custom heuristics:\n%s\nplayer: %s opponent: %s\n",
    #          game.to_string(), my_pos, op_pos)

    def _distance(point_x, point_y):
        return math.sqrt((point_x[0]-point_y[0])**2 + (point_x[1]-point_y[1])**2)

    def _distance_to_center(location):
        return _distance(location, center)

    def move_score_heuristic(factor):
        """move score heuristic - based on run data
        """
        if not factor:
            return factor

        score = 0
        idx = 0
        turn = game.__player_1__ == player
        for move in game.__history__:
            if turn:
                score += move_score[idx][move[0]][move[1]]
            turn = not turn
            idx += 1
            if idx > 2:
                break
        return factor*score

    def delta_move_heuristic(factor):
        """move heuristic calculation. gets the delta between moves
        """
        if not factor:
            return factor
        own_moves = len(game.get_legal_moves(player))
        opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
        score = own_moves - 2*opp_moves
        #LOG.debug("move_heuristic: %d", score)
        return factor*score

    def open_move_heuristic(factor):
        """number of open positions allowed to move for this player
        """
        if not factor:
            return factor
        return factor*len(game.get_legal_moves(player))

    def delta_central_heuristic(factor):
        """prefer moves to center
        """
        if not factor:
            return factor
        score = _distance_to_center(op_pos) - _distance_to_center(my_pos)
        #LOG.debug("delta_central_distance_heuristic: %d", score)
        return factor*score

    def central_distance_heuristic(factor):
        """prefer moves to center
        """
        if not factor:
            return factor
        score = _distance_to_center(my_pos)
        #LOG.debug("central_distance_heuristic: %d", score)
        return factor*score

    # heustics:
    heuristics = [
        (delta_move_heuristic, 1),
        #(open_move_heuristic, 0),
        (central_distance_heuristic, -1),
        #(delta_central_heuristic, 0),
        #(move_score_heuristic, 0)
        ]
    score = sum([h[0](h[1]) for h in heuristics])
    #LOG.debug(score)
    return float(score)


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

#pylint: disable-msg=too-many-arguments
    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', threshold=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.threshold = threshold
        self.playbook = lambda x, y: y

#pylint: enable-msg=too-many-arguments

    def playbook_move(self, game, legal_moves):
        """playbook for starting
        """
        return self.playbook(game, legal_moves)

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        def _move(depth):
            if self.method == 'minimax':
                score, move = self.minimax(game, depth)
            else:
                score, move = self.alphabeta(game, depth)
            return score, move

        #LOG.debug("get_move: \n%s\n%s", game.to_string(), legal_moves)
        self.time_left = time_left

        # if no legal moves return
        move = (-1, -1)
        if not legal_moves:
            #LOG.info("no legal moves:\n%s", game.to_string())
            return move

        # consult playbook
        moves = self.playbook_move(game, legal_moves)
        if len(moves) == 1:
            #LOG.debug("returning move: %s:\n%s", moves[0], game.to_string())
            return moves[0]

        depth = 1
        try:
            if self.iterative:
                while True:
                    score, move = _move(depth)
                    #LOG.debug("iterative deepening %d move: %s", depth, move)
                    if score in [float("inf"), float("-inf")]:
                        break
                    depth += 1
            else:
                _, move = _move(self.search_depth)
        except Timeout:
            # Handle any actions required at timeout, if necessary
            #LOG.error("Timedout waiting for search result (depth: %d):\n%s",
            #          depth, game.to_string())
            pass
        #LOG.debug("returning move: %s:\n%s", move, game.to_string())
        if self.iterative:
            search_depth.append(depth)
        return move

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        #LOG.debug("minimax vvvvv\n%s %d\n%s^^^^^^",
        #          "max" if maximizing_player else "min",
        #          depth, game.to_string())
        if self.time_left() < self.threshold:
            raise Timeout()
        if depth == 0 or not game.get_legal_moves():
            return self.score(game, self), None

        ply = [(self.minimax(game.forecast_move(move), \
                depth-1, not maximizing_player)[0], move) \
               for move in game.get_legal_moves()]
        #LOG.debug("minimax %d %d.%s", depth, len(ply), ply)
        bestof = max if maximizing_player else min
        best = bestof(ply, key=lambda x: x[0])
        #equivalents = [m for m in ply if m[0] == best[0]]
        #return equivalents[randint(0, len(equivalents) - 1)]
        return best

#pylint: disable-msg=too-many-arguments
    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"),
                  maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        #LOG.debug("alphabeta vvvvv\n%s %d α:%d β:%d\n%s^^^^^^",
        #          "max" if maximizing_player else "min",
        #          alpha, beta,
        #          depth, game.to_string())

        if self.time_left() < self.threshold:
            raise Timeout()
        if depth == 0 or not game.get_legal_moves():
            return self.score(game, self), None

        best = float("-inf") if maximizing_player  else float("inf")
        bestmove = (-1, -1)
        bestof = max if maximizing_player else min
        ply = []
        for move in game.get_legal_moves():
            value, _ = self.alphabeta(game.forecast_move(move), depth-1,
                                      alpha, beta, not maximizing_player)
            ply.append((value, move))
            best = bestof([value, best])
            if best == value:
                bestmove = move
                if maximizing_player:
                    alpha = bestof(alpha, best)
                    if best >= beta:
                        break
                else:
                    beta = bestof(beta, best)
                    if best <= alpha:
                        break
        #equivalents = [m for m in ply if m[0] == best]
        #return equivalents[randint(0, len(equivalents) - 1)]
        return best, bestmove
#pylint: enable-msg=too-many-arguments
