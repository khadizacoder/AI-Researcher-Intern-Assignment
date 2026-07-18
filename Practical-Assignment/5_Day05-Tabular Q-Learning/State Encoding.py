import random
import numpy as np
import matplotlib.pyplot as plt

#! Environment

grid_size = 5
target = (grid_size - 1, grid_size - 1)

agent_row = random.randint(0, grid_size-1)
agent_col = random.randint(0, grid_size-1)

while (agent_row, agent_col) == target:
    agent_row = random.randint(0, grid_size-1)
    agent_col = random.randint(0, grid_size-1)

pickup_row = random.randint(0, grid_size-1)
pickup_col = random.randint(0, grid_size-1)

while ((pickup_row, pickup_col) == (agent_row, agent_col) or (pickup_row, pickup_col) == target):
    pickup_row = random.randint(0, grid_size-1)
    pickup_col = random.randint(0, grid_size-1)


carrying = False

for row in range(grid_size):
    for col in range(grid_size):
        if (row, col) == (agent_row, agent_col):
            print("🤖", end=" ")
        elif (row, col) == (pickup_row, pickup_col):
            print("📦", end=" ")
        elif (row, col) == target:
            print("🎯", end=" ")
        else: print("🔘", end=" ") #🟡
    print()
   
state = (
    (agent_row, agent_col),
    (pickup_row, pickup_col),
    carrying
)
# print(state)

actions = [
    (-1, 0),     # Up
    (1, 0),      # Down
    (0, -1),     # Left
    (0, 1),      # Right
    (-1, -1),    # UpLeft
    (-1, 1),     # UpRight
    (1, -1),     # DownLeft
    (1, 1)       # DownRight
]

# print(agent_row, agent_col)
move_row, move_col = actions[5]

new_row = agent_row + move_row
new_col = agent_col + move_col

# print(new_row, new_col)
if 0 <= new_row < grid_size and 0 <= new_col < grid_size :
    agent_row = new_row
    agent_col = new_col
    print("Move Successful")
else : print("Invalid Move")


#! Q-Table

num_positions = grid_size * grid_size
num_states = num_positions * num_positions * 2
num_actions = 8
q_table = np.zeros((num_states, num_actions))


def encode_state(agent_row, agent_col,
                 pickup_row, pickup_col,
                 carrying):

    agent_index = agent_row * grid_size + agent_col

    pickup_index = pickup_row * grid_size + pickup_col

    carrying_value = int(carrying)

    state = (
        (agent_index * num_positions + pickup_index)
        * 2
        + carrying_value
    )

    return state