import random

# Topic 1: Grid World --> ৫×৫ Environment তৈরি করা যেখানে Agent Move করবে
grid_size = 5
target = (grid_size -1, grid_size-1)

# Topic 2: Agent --> Grid-এর মধ্যে Agent-কে Random Position-এ বসানো।
agent_row = random.randint(0, grid_size-1)
agent_col = random.randint(0, grid_size-1)


while (agent_row, agent_col) == target :
    agent_row = random.randint(0, grid_size-1)
    agent_col = random.randint(0, grid_size-1)
    

# Topic 3 : Pickup Location
pickup_row = random.randint(0, grid_size-1)
pickup_col = random.randint(0, grid_size-1)

while (pickup_row, pickup_col) == (agent_row, agent_col) or (pickup_row, pickup_col) == target:
    pickup_row = random.randint(0, grid_size-1)
    pickup_col = random.randint(0, grid_size-1)
    
# Topic 4 : Grid Print
for row in range(grid_size):
    for col in range(grid_size):
        if((row, col) == (agent_row, agent_col)):
            print('A', end=" ")
        elif((row, col) == (pickup_row, pickup_col)):
            print('P', end=" ")
        elif((row, col) == target):
            print('G', end=" ")
        else: print('.', end=" ")
    print()
        
# Topic 5 : Carrying
carrying = False

# Topic 6 : Action & Movement
# action = "right"
# move_row = 0
# move_col = 0

# if action == 'up':
#     move_row = -1
# elif action == 'down':
#     move_row = 1
# elif action == 'left':
#     move_col = -1
# elif action == 'right':
#     move_col = 1
    
# new_row = agent_row + move_row
# new_col = agent_col + move_col
reward = 0

# Normal Move      = -1
# Pickup           = +10
# Goal Delivery    = +100
# Invalid Move     = -5

def step(action):
    
    global agent_row
    global agent_col
    global carrying
    global reward
    
    move_row = 0
    move_col = 0

    if action == 'up':
        move_row = -1
    elif action == 'down':
        move_row = 1
    elif action == 'left':
        move_col = -1
    elif action == 'right':
        move_col = 1
    elif action == "up_right":
        move_row = -1
        move_col = 1
    elif action == "up_left":
        move_row = -1
        move_col = -1
    elif action == "down_right":
        move_row = 1
        move_col = 1
    elif action == "down_left":
        move_row = 1
        move_col = -1
        
    new_row = agent_row + move_row
    new_col = agent_col + move_col


    
    if 0 <= new_row < grid_size and 0 <= new_col < grid_size:
        agent_row = new_row
        agent_col = new_col
        reward = -1
        
        if(agent_row, agent_col) == (pickup_row, pickup_col) and not carrying:
            reward = 10
            carrying = True
        
        if(agent_row, agent_col) == target and carrying:
            reward = 100
            carrying = False

    else : 
        reward = -5

    return reward


reward = step("right")
print("Reward:", reward)
print("Agent:", agent_row, agent_col)
