"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random
import logging
from collections import deque
from scorefunctions import custom_score

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


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

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10., quiessant_search=False):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        self.quiessant_search = quiessant_search
#         self.logger = logging.getLogger('customplayer')

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

        self.time_left = time_left
        
        options = game.get_legal_moves()
        assert options == legal_moves, "Mismatched moves"

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves

        score, move = None, random.choice(legal_moves) if len(legal_moves) > 0 else None
        try:
            # Iterative deepening with Quiessance search:
            if self.iterative is True:
                results = deque(maxlen=3)
                for depth in range (self.search_depth, 25):
                    score, move = self.dosearch(game, depth)
                    results.append((score, move))
                    if self.quiessant_search is True:
                        if len(results) >=3 and all(x[1] == move for x in results):
                            break
                    elif score == float('-inf') or score == float ('inf'):
                        break
                    if self.time_left() < self.TIMER_THRESHOLD:
                        break
            else:
                score, move = self.dosearch(game, self.search_depth)
                assert score is not None
                
            if len (options) > 0:
                assert not (move is None or move is (-1,-1)), "Move ({}, {}) for '{}/{}' cannot be None or (-1,-1) if options ({}) exist".format(move, score, self.method, self.score, options)
                assert move in options, "Move ({}, {}) for '{}/{}' not from existing list of moves ({})".format(move, score, self.method, self.score, options)
        except Timeout:
            # Handle any actions required at timeout, if necessary
            pass

        # Return the best move from the last completed search
        # (or iterative-deepening search iteration)
        return move
    
    def dosearch(self, game, depth):
        if self.method == 'minimax':
            mm_s, mm_m = self.minimax(game, depth)
            return mm_s, mm_m
        else: # alphabeta
            ab_s, ab_m = self.alphabeta(game, depth)
            return ab_s, ab_m

    def minimax(self, game, depth, maximizing_player=True, tab='\t'):
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
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        legal_moves = game.get_legal_moves(game.active_player)
        if legal_moves is not None and len(legal_moves)>0:
            if depth>0: # Recursive case:
                if maximizing_player:   # MAXIMIZING ply
                    score, move = None, None
                    for i,m in enumerate(legal_moves):
                        newscore, _ = self.minimax(game.forecast_move(m), depth-1, maximizing_player=not maximizing_player, tab=tab+'\t')
                        if score is None or newscore > score:
                            score, move = newscore, m
                else:                   # MINIMIZING ply
                    score, move = None, None
                    for i,m in enumerate(legal_moves):
                        newscore, _ = self.minimax(game.forecast_move(m), depth-1, maximizing_player=not maximizing_player, tab=tab+'\t')
                        if score is None or newscore < score:
                            score, move = newscore, m
            else: # Base case (depth==0)
                score, move = self.score(game, self), None
        else:  # We are at a DEAD-END here
            score, move = self.score(game, self), (-1, -1)

        return score, move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True, tab='\t'):
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
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        floor = alpha
        ceiling = beta
        legal_moves = game.get_legal_moves(game.active_player)
        if legal_moves is not None and len(legal_moves)>0:
            if depth>0: # Recursive case:
                if maximizing_player:   # MAXIMIZING ply
                    score, move = None, None
                    for i,m in enumerate(legal_moves):
                        newscore, _ = self.alphabeta(game.forecast_move(m), depth-1, floor, ceiling, maximizing_player=not maximizing_player, tab=tab+'\t')
                        if score is None or newscore > score:
                            score, move = newscore, m
                            
                        # Alphabeta bookkeeping:
                        if score > floor:
                            floor = score   # Constrains children at the next (minimizing) layer to be above this value
                        if score >= ceiling: # No need to search any more if we've crossed the upper limit at this max layer already
                            break
                else:                   # MINIMIZING ply
#                     print (tab + "MINIMIZING: (({})) {} < score < {}  ||  Moves: {}".format(depth, floor, ceiling, legal_moves))
                    score, move = None, None
                    for i,m in enumerate(legal_moves):
                        newscore, _ = self.alphabeta(game.forecast_move(m), depth-1, floor, ceiling, maximizing_player=not maximizing_player, tab=tab+'\t')
                        if score is None or newscore < score:
                            score, move = newscore, m
                            
                        # Alphabeta bookkeeping:
                        if score < ceiling:
                            ceiling = score   # Constrains children at the next (maximizing) layer to be below this value
                        if score <= floor: # No need to search any more if we've crossed the lower limit at this min layer already
                            break
            else: # Base case (depth==0)
                score, move = self.score(game, self), None
        else: # We are at a DEAD-END here
            score, move = self.score(game, self), (-1, -1)

        return score, move