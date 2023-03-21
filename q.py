import random
import time
import csv


class Environment():

    def __init__(self, p1=0.2, p2=0.2):
        self.probability_go_to_desired = p1
        self.probability_stay = p2
        self.goal_square = (9, 9)  # top right corner
        grid_size = 10
        '''
        Walls are defined by what direction that prevent movement
        For example if a cell had a wall above it and to it's left
        (the top left corned of the gridworld) then the cell would 
        be 'ul' to represent that it can't go up and it can't go 
        left in this position.
        u = up
        d = down
        l = left
        r = right
        '''
        self.walls = [['']*grid_size for _ in range(grid_size)]
        for x in range(grid_size):
            self.walls[0][x] += 'd'  # bottom of the world
            self.walls[grid_size-1][x] += 'u'  # top of the world
            self.walls[x][0] += 'l'  # left side of world
            self.walls[x][grid_size-1] += 'r'  # right side of world

            # Vertical middle wall
            self.walls[4][x] += 'u'
            self.walls[5][x] += 'd'
            self.walls[4][2] = ''  # door way 1
            self.walls[5][2] = ''  # door way 1
            self.walls[4][7] = ''  # door way 2
            self.walls[5][7] = ''  # door way 2
            # horizontal middle wall
            self.walls[x][4] += 'r'
            self.walls[x][5] += 'l'
            self.walls[2][4] = ''  # door way 3
            self.walls[2][5] = ''  # door way 3
            self.walls[7][4] = ''  # door way 4
            self.walls[7][5] = ''  # door way 4

    def agent_makes_decision(self, action, state):
        '''
        action (string): 'up' or 'down' or 'left' or 'right
        state (tuple): pairwise (row,column) corrdinates
        '''
        action_lookup = {
            'up': 'u',
            'down': 'd',
            'right': 'r',
            'left': 'l'
        }
        if not action in action_lookup:
            raise Exception("not recognized action!")
        stocastic_decision = random.uniform(0, 1)
        moves = []
        if stocastic_decision <= self.probability_go_to_desired:
            moves = [action_lookup[action]]
        elif stocastic_decision-self.probability_go_to_desired <= self.probability_stay:
            pass
        else:
            choose_left = random.uniform(0, 1)
            if choose_left <= 0.5:
                left_lookup = {
                    'up': 'l',
                    'down': 'r',
                    'right': 'u',
                    'left': 'd'
                }
                moves = [action_lookup[action], left_lookup[action]]
            else:
                right_lookup = {
                    'up': 'r',
                    'down': 'l',
                    'right': 'd',
                    'left': 'u'
                }
                moves = [action_lookup[action], right_lookup[action]]

        return self.agent_moves(moves=moves, state=state)

    def agent_moves(self, moves, state):
        '''
        moves(array): containes 'u','d','l','r'
        state (tuple): pairwise (row,column) corrdinates
        '''
        move_effect = {
            'u': lambda row, col:  (row+1, col),
            'd': lambda row, col:  (row-1, col),
            'l': lambda row, col: (row, col-1),
            'r': lambda row, col: (row, col+1),
        }
        row, col = state
        for move in moves:
            if not move in self.walls[row][col]:
                row, col = move_effect[move](row, col)

        if row == self.goal_square[0] and col == self.goal_square[1]:
            return {
                'reward': 100,
                'location': (row, col)
            }
        else:
            return {
                'reward': -1,
                'location': (row, col)
            }

# ////////////////////////////////
# FINISHED ENVIRONMENT DECLARATION
# ////////////////////////////////


# ------ GLOBAL VARIABLES ---------
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.1
NUM_EPISODES = 100000

standard_input = '1\n0'
user_input = {}
user_input_labels = ['p1', 'p2']
# Get user input
for label in user_input_labels:
    print(f'Enter a number for {label}')
    user_input[label] = float(input())

# ////////////////////////////////
#    START Q LEARNING LOGIC
# ////////////////////////////////


def generate_matrix(initialized_value):
    new_matrix = {}
    grid_size = 10
    for col in range(grid_size):
        for row in range(grid_size):
            new_matrix[(row, col)] = {}
            for action in ['up', 'down', 'left', 'right']:
                new_matrix[(row, col)][action] = initialized_value
    return new_matrix


def random_start_state():
    return (random.randint(0, 9), random.randint(0, 9))


def choose_max_Q(Qs, e=EPSILON):
    maxA = ''
    maxQ = -1000
    actions = ['up', 'down', 'left', 'right']
    if random.random() < e:
        maxA = actions[random.randint(0, 3)]
        return maxA, Qs[maxA]
    for a in actions:
        if Qs[a] > maxQ:
            maxQ = Qs[a]
            maxA = a

    return maxA, maxQ


def see_action_values(Q):
    for r in range(10):
        line = []
        if r == 5:
            line = ['--------', '--------', '        ', '--------', '--------',
                    '+-------', '--------', '--------', '        ', '--------', '--------']
            format = len(line)*'{:8s}'
            print(format.format(*line))
        line = []
        for c in range(10):
            if c == 5:
                line.append(' ') if r == 2 or r == 7 else line.append('|')
            best_action, best_action_value = choose_max_Q(Q[(9-r, c)])
            line.append(str(round(best_action_value, 2))+' ')
        format = len(line)*'{:8s}'
        print(format.format(*line))


def see_policy(Q):
    for r in range(10):
        line = []
        if r == 5:
            line = ['--------', '--------', '        ', '--------', '--------',
                    '+-------', '--------', '--------', '        ', '--------', '--------']
            format = len(line)*'{:8s}'
            print(format.format(*line))
        line = []
        for c in range(10):
            if c == 5:
                line.append(' ') if r == 2 or r == 7 else line.append('|')
            best_action, best_action_value = choose_max_Q(Q[(9-r, c)])
            line.append(best_action)
        format = len(line)*'{:8s}'
        print(format.format(*line))


def Q_learning():
    env = Environment()
    Q = generate_matrix(0)
    total_steps = 0
    for i in range(NUM_EPISODES):
        state = random_start_state()
        while True:
            if state == (9, 9):
                break
            best_action, best_action_value = choose_max_Q(Q[state])
            move = env.agent_makes_decision(best_action, state)
            state_prime = move['location']
            max_next_action, max_next_state_action_value = choose_max_Q(
                Q[state_prime])
            learning_step_value = ALPHA * \
                (move['reward']+GAMMA*max_next_state_action_value-best_action_value)
            Q[state][best_action] = Q[state][best_action] + learning_step_value
            state = state_prime
            total_steps += 1
    return Q, total_steps
# ////////////////////////////////
#    END Q LEARNING LOGIC
# ////////////////////////////////


start_time = time.time()
Q, steps = Q_learning()
see_action_values(Q)
see_policy(Q)
print(f'done. Finished in {time.time() - start_time} with {steps} steps')
