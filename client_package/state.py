import logging
from enum import Enum

class State(Enum):
    ERROR = 0           # Default value, shouldn't be at 0 for any reason
    LOGIN = 1           # After connection, state is switched to 1, waiting on server response
    CLIENT_INPUT = 2    # Acknowledged server response, awaiting client input
    START_WAITING = 3   # Selected start, waiting for another player to join
    JOIN_WAITING = 4    # Selected join, waiting for server response of game join
    BEGIN = 5           # Server joined both clients into 1 game, begin next state
    PLAYER_TURN = 6     # Current player's move
    PLAYER_WAITING = 7  # Current player waiting on opponents move
    END_GAME_WIN = 8    # Game concluded for both player's display results, return to 2
    END_GAME_LOSS = 10
    QUIT = 9            # Player quit, shut game down and remove player
    ESTABLISH = 99      # Initial state when client/server first interact


# current_state = None

# ["search", "login", "start", "join", "move", "quit"]

# class State:
#     def __init__(self):
#         logging.info(f"Initalizing client state.")
#         self.possible_actions = ["search", "login", "start", "join", "move", "quit"]
#         self.possible_joins = []

#     def get_next_states(self, content):
#         self.update_actions(content)
#         logging.info(f"retrieving states {self.possible_actions}")
#         return self.possible_actions
    
#     def get_actions(self):
#         return self.possible_actions
    
#     def get_possible_joins(self):
#         logging.info(f"Retrieving possible joins: {self.possible_joins}")
#         return self.possible_joins

#     def set_possible_joins(self, list_joins):
#         logging.info(f"Setting list of joins as: {list_joins}")
#         self.possible_joins = list_joins
    
#     def add_possible_join(self, username):
#         logging.info(f"Adding username {username} to list of possible joins.")
#         self.possible_joins.append(username)
    
#     def update_actions(self, action):
#         logging.info(f"Update Actions with {action}, before: {self.possible_actions}")
#         if action == 'login':
#             self.possible_actions.remove('login')
#             self.possible_actions.remove('move')
#         elif action == 'start':
#             self.possible_actions.remove('start')
#             self.possible_actions.remove('join')
#         elif action == 'join':
#             if self.possible_joins != None:
#                 self.possible_actions = self.possible_joins
#             else:
#                 self.no_join()
#         logging.info(f"Update Actions with {action}, after: {self.possible_actions}")

#     def no_join(self):
#         self.possible_actions = ["search", "start", "join", "quit"]
#         logging.info(f"No possible joins. New actions: {self.possible_actions}")
#         return self.possible_actions
        