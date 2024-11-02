current_state = None

# ["search", "login", "start", "join", "move", "quit"]

class State:
    def __init__(self):
        self.possible_actions = ["search", "login", "start", "join", "move", "quit"]
        self.possible_joins = None

    def get_next_states(self, content):
        self.update_actions(content)
        return self.possible_actions
    
    def get_possible_joins(self):
        return self.possible_joins

    def set_possible_joins(self, list_joins):
        self.possible_joins = list_joins
    
    def update_actions(self, action):
        if action == 'login':
            self.possible_actions.remove('login')
            self.possible_actions.remove('move')
        elif action == 'start':
            self.possible_actions.remove('start')
            self.possible_actions.remove('join')
        elif action == 'join':
            self.possible_actions = self.possible_joins

    def no_join(self):
        self.possible_actions = ["search", "start", "join", "quit"]
        return self.possible_actions
        