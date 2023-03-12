import random
import unittest


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

    def agent_makes_decision(self, action, state, unit_test_var=None, unit_test_left=None):
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
        stocastic_decision = random.uniform(0, 1) if (
            unit_test_var is None) else unit_test_var
        moves = []
        if stocastic_decision <= self.probability_go_to_desired:
            moves = [action_lookup[action]]
        elif stocastic_decision-self.probability_go_to_desired <= self.probability_stay:
            pass
        else:
            choose_left = random.uniform(0, 1) if (
                unit_test_left is None) else unit_test_left
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


class TestMethods(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestMethods, self).__init__(*args, **kwargs)
        self.env = Environment()

    def test_wall_desired(self):
        results = self.env.agent_makes_decision('up', (5, 5), unit_test_var=0)
        self.assertEqual(results['location'], (6, 5))
        results = self.env.agent_makes_decision('up', (9, 5), unit_test_var=0)
        self.assertEqual(results['location'], (9, 5))
        results = self.env.agent_makes_decision('up', (4, 5), unit_test_var=0)
        self.assertEqual(results['location'], (4, 5))
        results = self.env.agent_makes_decision(
            'left', (0, 0), unit_test_var=0)
        self.assertEqual(results['location'], (0, 0))
        results = self.env.agent_makes_decision(
            'right', (0, 0), unit_test_var=0)
        self.assertEqual(results['location'], (0, 1))
        results = self.env.agent_makes_decision(
            'down', (0, 0), unit_test_var=0)
        self.assertEqual(results['location'], (0, 0))

    def test_wall_stay(self):
        results = self.env.agent_makes_decision(
            'up', (4, 5), unit_test_var=0.4)
        self.assertEqual(results['location'], (4, 5))
        results = self.env.agent_makes_decision(
            'down', (4, 5), unit_test_var=0.4)
        self.assertEqual(results['location'], (4, 5))
        results = self.env.agent_makes_decision(
            'right', (4, 5), unit_test_var=0.4)
        self.assertEqual(results['location'], (4, 5))
        results = self.env.agent_makes_decision(
            'left', (4, 5), unit_test_var=0.4)
        self.assertEqual(results['location'], (4, 5))

    def test_wall_side_step(self):
        results = self.env.agent_makes_decision(
            'up', (5, 5), unit_test_var=0.5, unit_test_left=0)
        self.assertEqual(results['location'], (6, 5))
        results = self.env.agent_makes_decision(
            'up', (5, 5), unit_test_var=0.5, unit_test_left=1)
        self.assertEqual(results['location'], (6, 6))
        results = self.env.agent_makes_decision(
            'up', (4, 2), unit_test_var=0.5, unit_test_left=0)
        self.assertEqual(results['location'], (5, 1))
        results = self.env.agent_makes_decision(
            'left', (4, 2), unit_test_var=0.5, unit_test_left=1)
        self.assertEqual(results['location'], (4, 1))

    def test_reward(self):
        results = self.env.agent_makes_decision(
            'up', (3, 4), unit_test_var=0.5, unit_test_left=0)
        self.assertEqual(results['reward'], -1)
        results = self.env.agent_makes_decision('up', (8, 9), unit_test_var=0)
        self.assertEqual(results['reward'], 100)


if __name__ == '__main__':
    unittest.main()
