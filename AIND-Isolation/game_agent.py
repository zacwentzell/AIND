"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random

from functools import partial
from numpy import sqrt


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def sign(num):
    return -1 if num < 0 else 1


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

    # TODO: finish this function!
    opponent = game.get_opponent(player)

    player_moves = game.get_legal_moves(player)
    num_player_moves = len(player_moves)

    opponent_moves = game.get_legal_moves(opponent)
    num_opponent_moves = len(opponent_moves)
    board_covered = 1 - (len(game.get_blank_spaces())/float(game.height*game.width))

    # if player wins, measure win value by number of moves remaining
    if num_player_moves == 0 and (player == game.active_player or num_opponent_moves > 0):
        return float("-inf")
    elif num_opponent_moves == 0:
        return 100000 + num_player_moves

    player_next_moves = sum([game.__get_moves__(move) for move in game.get_legal_moves(player)], [])
    opponent_next_moves = sum([game.__get_moves__(move) for move in game.get_legal_moves(opponent)], [])

    # player_last_move = game.get_player_location(player)
    # opponent_last_move = game.get_player_location(player)

    # plm_r, plm_c = player_last_move
    # olm_r, olm_c = opponent_last_move

    # player_empty_spaces_nearby = sum([(plm_r - i, plm_c - j) in game.get_blank_spaces() for i in [-2, -1, 0, 1, 2] for j in [-2, -1, 0, 1, 2]])
    # opp_empty_spaces_nearby = sum([(olm_r - i, olm_c - j) in game.get_blank_spaces() for i in [-2, -1, 0, 1, 2] for j in [-2, -1, 0, 1, 2]])
    # distance_to_opponent = abs(plm_r - olm_r) + abs(plm_c - olm_c)
    # distance_to_center = sqrt((plm_r-game.height)**2 + (plm_c-game.width)**2)
    move_diff = num_player_moves - num_opponent_moves

    # return sign(move_diff)*(move_diff)**2 + len(player_next_moves) - len(opponent_next_moves)
    # return move_diff + sign(move_diff)*max(num_player_moves/num_opponent_moves, num_opponent_moves/num_player_moves) #+ 2*len(player_next_moves)
    # return move_diff + sign(move_diff) * max(num_player_moves / num_opponent_moves, num_opponent_moves / num_player_moves)*100.0 - distance_to_opponent
    # calc_1 = ((num_player_moves - num_opponent_moves) / min(num_player_moves, num_opponent_moves))
    return (len(player_next_moves) - len(opponent_next_moves))**3 + move_diff


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
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def __repr__(self):
        return 'CustomPlayer - {}, {}'.format(self.method, self.score.__name__)

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
        def all_the_time():
            return 10000

        # self.time_left = all_the_time
        self.time_left = time_left


        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves

        if legal_moves:
            best_move, utility = random.choice(legal_moves), 0.0
        else:
            best_move, utility = (-1, -1), float('-inf')

        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            max_depth_reached = 0

            if self.iterative:
                while True:
                    non_leaves=[]
                    utility, best_move = getattr(self, self.method)(game=game, depth=max_depth_reached + 1, non_leaves=non_leaves)
                    max_depth_reached += 1
                    if not non_leaves:
                        break
            else:
                utility, best_move = getattr(self, self.method)(game=game, depth=self.search_depth)


        except Timeout:
            # Handle any actions required at timeout, if necessary
            pass

        # Return the best move from the last completed search iteration
        # print('Player: {}, Max Depth Reached: {}, Utility: {}'.format(self, max_depth_reached, utility))
        return best_move

    def minimax(self, game, depth, maximizing_player=True, non_leaves=None):
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

        moves = game.get_legal_moves()

        if depth == 0:
            if non_leaves==[]:
                non_leaves.append(1)
            return self.score(game, self), game.__last_player_move__[game.inactive_player]

        if len(moves) == 0:
            return self.score(game, self), (-1, -1)

        else:
            values = []

            for move in moves:
                forecast = game.forecast_move(move)
                # print(forecast.to_string())
                utility, next_move = self.minimax(game=forecast,
                                                  depth=depth-1,
                                                  maximizing_player=not maximizing_player,
                                                  non_leaves=non_leaves)
                values.append((utility, move))
            if maximizing_player:
                return max(values, key=lambda x: x[0])
            else:
                return min(values, key=lambda x: x[0])




    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True, non_leaves=None):
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

        moves = game.get_legal_moves()

        if depth == 0:
            if non_leaves == []:
                non_leaves.append(1)
            return self.score(game, self), (-1, -1)

        if len(moves) == 0:
            return self.score(game, self), (-1, -1)

        else:
            values = []

            for move in moves:
                forecast = game.forecast_move(move)
                # print(forecast.to_string())
                utility, next_move = self.alphabeta(game=forecast,
                                                    depth=depth-1,
                                                    alpha=alpha,
                                                    beta=beta,
                                                    maximizing_player=not maximizing_player,
                                                    non_leaves=non_leaves)
                if maximizing_player:
                    if utility > alpha:
                        alpha = utility
                    if utility >= beta:
                        return utility, move
                else:
                    if utility < beta:
                        beta = utility
                    if utility <= alpha:
                        return utility, move
                values.append((utility, move))
            if maximizing_player:
                return max(values, key=lambda x: x[0])
            else:
                return min(values, key=lambda x: x[0])

