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
            self.walls[grid_size-1][x] += 'u'  # top fo the world
            self.walls[x][0] += 'l'  # left side of world
            self.walls[x][grid_size-1] += 'r'  # right sid eof world

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


a = 0.1
g = 0.9
EPSILON = 0.1
NUM_EPISODES = 1000
ALPHA = 0.1
GAMMA = 0.9
recorded_times = []

standard_input = '1\n0'
user_input = {}
user_input_labels = ['p1', 'p2']
# Get user input
for label in user_input_labels:
    print(f'Enter a numer for {label}')
    user_input[label] = float(input())


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


def choose_max_Q(Qs):
    maxA = ''
    maxQ = -1000
    actions = ['up', 'down', 'left', 'right']
    if random.random() < EPSILON:
        maxA = actions[random.randint(0, 3)]
        return maxA, Qs[maxA]
    for a in actions:
        if Qs[a] > maxQ:
            maxQ = Qs[a]
            maxA = a

    return maxA, maxQ


def see_action_values(Q):
    for c in range(10):
        line =[]
        if c == 5:
            line=['--------','--------','        ','--------','--------','+-------','--------','--------','        ','--------','--------']
            format = len(line)*'{:8s}'
            print(format.format(*line))
        line = []
        for r in range(10):
            if r== 5:
                line.append(' ') if c==2 or c==7 else line.append('|')
            best_action, best_action_value = choose_max_Q(Q[(r, 9 - c)])
            line.append(str(round(best_action_value,2))+' ')
            # print('%s' % (best_action)+' ',end='')
        format = len(line)*'{:8s}'
        print(format.format(*line))



def find_a_star(Q, state):
    row, col = state
    Q_at_cell = Q[(row, col)]
    max_action = max(Q_at_cell.items(), key=lambda item: item[1])[0]
    return max_action


def sarsa():
    env = Environment()
    Q = generate_matrix(0)
    last_time = time.time()
    for i in range(NUM_EPISODES):
        starting_point = random_start_state()
        state = starting_point
        while True:
            best_action = max(Q[state].items(), key=lambda item: item[1])[
                0]  # make e-greedy
            move = env.agent_makes_decision(best_action, state)
            if state == (9, 9):
                break
            state_prime = move['location']
            max_next_action = max(Q[state_prime].items(),
                                  key=lambda item: item[1])[0]
            learning_step_value = ALPHA * \
                (move['reward']+GAMMA*Q[state_prime]
                 [max_next_action]-Q[state][best_action])
            Q[state][best_action] = Q[state][best_action] + learning_step_value
            state = state_prime
        time_delta = time.time() - last_time
        recorded_times.append((i, time_delta))
        last_time = time.time()
    return Q


start_time = time.time()
Q = sarsa()

# see_action_values(Q)
print(
    f"Elapsed time {time.time() - start_time} with times of \n{len(recorded_times)}")


def Q_to_2D(Q):
    grid_size = 10
    grid = [[0]*grid_size for x in range(grid_size)]
    for state, action_dict in Q.items():
        row, col = state
        grid[row][col] = str(max(action_dict.values()))
    grid.reverse()
    return grid


with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(Q_to_2D(Q))

print('done')
