a = 0.1
g = 0.9
e = 0.1

standard_input = '1\n0'
user_input = {}
user_input_labels = ['p1','p2']
# Get user input
for label in user_input_labels:
    print(f'Enter a numer for {label}')
    user_input[label] = float(input())