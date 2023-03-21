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


a = 0.1
GAMMA = 0.9
EPSILON = 0.1
NUM_EPISODES = 100000
MAX_EPISODE_DEPTH = 50000
recorded_times = []

standard_input = '1\n0\n'
user_input = {}
user_input_labels = ['p1', 'p2']
# Get user input
for label in user_input_labels:
    print(f'Enter a number for {label}')
    user_input[label] = float(input())


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
            # line.append(str(round(best_action_value,2))+' ')
            line.append(best_action)
        format = len(line)*'{:8s}'
        print(format.format(*line))


def random_start_state():
    return (random.randint(0, 9), random.randint(0, 9))


def generate_matrix(initialized_value):
    new_matrix = {}
    grid_size = 10
    for col in range(grid_size):
        for row in range(grid_size):
            new_matrix[(row, col)] = {}
            for action in ['up', 'down', 'left', 'right']:
                new_matrix[(row, col)][action] = initialized_value
    return new_matrix


def choose_max_Q(Qs):
    maxA = ''
    maxQ = -1000
    for a in ['up', 'down', 'left', 'right']:
        if Qs[a] > maxQ:
            maxQ = Qs[a]
            maxA = a
    return maxA, maxQ


def epsilon_greedy_policy(Q):
    policy = {}
    for c in range(10):
        for r in range(10):
            policy[(r, c)] = choose_max_Q((Q[(r, c)]))
    return policy


def generate_episode(policy, env):
    episode = []
    state = random_start_state()
    for _ in range(MAX_EPISODE_DEPTH):
        cell_policy = policy[state].items()
        action = random.choices([x[0] for x in cell_policy], [
                                x[1] for x in cell_policy])[0]
        move = env.agent_makes_decision(action, state)
        reward = move['reward']
        episode.append([state, action, reward])
        state = move['location']
        if reward == 100:
            break
    # print(ep_length)
    return episode


def process_policy(episode, Q, return_sum, return_count):
    G = 0
    previous_state_actions = set()
    episode_return_values = []
    for state, action, reward in episode[::-1]:
        G = GAMMA*G + reward
        episode_return_values.append([state, action, G])
    # episode_return_values.reverse()
    for state, action, reward in episode[::-1]:
        if state != (9, 9) and not state in previous_state_actions:
            previous_state_actions.add(state)
            return_sum[state][action] += G
            return_count[state][action] += 1
            Q[state][action] = return_sum[state][action] / \
                return_count[state][action]


def find_a_star(Q, state):
    row, col = state
    Q_at_cell = Q[(row, col)]
    max_action = max(Q_at_cell.items(), key=lambda item: item[1])[0]
    return max_action


def make_new_policy_for_cell(a_star):
    num_of_actions = 4
    return {
        'up': (1-EPSILON) + EPSILON/num_of_actions if a_star == 'up' else EPSILON/num_of_actions,
        'down': (1-EPSILON) + EPSILON/num_of_actions if a_star == 'down' else EPSILON/num_of_actions,
        'left': (1-EPSILON) + EPSILON/num_of_actions if a_star == 'left' else EPSILON/num_of_actions,
        'right': (1-EPSILON) + EPSILON/num_of_actions if a_star == 'right' else EPSILON/num_of_actions,
    }


def update_policy(episode, Q, policy):
    unique_states_in_episode = [e[0] for e in episode]
    for state in unique_states_in_episode:
        greedy_action = find_a_star(Q, state)
        policy[state] = make_new_policy_for_cell(greedy_action)


def mc_control():
    env = Environment(p1=user_input['p1'], p2=user_input['p2'])
    Q = generate_matrix(-10)
    return_sum = generate_matrix(0)
    return_count = generate_matrix(0)
    policy = generate_matrix(0.25)
    last_time = time.time()
    for i in range(NUM_EPISODES):
        episode = generate_episode(policy, env)
        process_policy(episode, Q, return_sum, return_count)
        update_policy(episode, Q, policy)
        time_delta = time.time() - last_time
        recorded_times.append((i, time_delta))
        last_time = time.time()
    return Q


start_time = time.time()
print('start')
Q = mc_control()
see_action_values(Q)
print(f"Elapsed time {time.time() - start_time} with {NUM_EPISODES} episodes")
print('done')
