from environment import Environment

env = Environment(p1=1, p2=0)
state = (0, 0)
while True:
    moves = input()
    move = ''
    if moves == 'w':
        move = 'up'
    elif moves == 'a':
        move = 'left'
    elif moves == 'd':
        move = 'right'
    elif moves == 's':
        move = 'down'
    response = env.agent_makes_decision(move, state)
    row, col = response['location']
    state = response['location']
    for x in range(9, -1, -1):
        for y in range(10):
            if row == x and col == y:
                print('*', end='')
            else:
                print('-', end='')
        print('')
