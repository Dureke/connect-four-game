current_state = None

# ["search", "login", "start", "join", "move", "quit"]

class State:
    def __init__(self):
        self.possible_actions = ["search", "login", "start", "join", "move", "quit"]

    def get_next_states(self, content):
        self.update_actions(content['action'])
        return self.possible_actions
    
    def update_actions(self, action):
        if action == 'login':
            self.possible_actions.remove('login')
            self.possible_actions.remove('move')
        elif action == 'start':
            self.possible_actions.remove('start')
            self.possible_actions.remove('join')
        