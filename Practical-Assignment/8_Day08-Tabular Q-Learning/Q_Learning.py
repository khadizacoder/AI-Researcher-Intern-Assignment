import numpy as np # Mathematical Library
import matplotlib.pyplot as plt # Graph আঁকার Library
from enum import IntEnum # Number-এর মতো আচরণ করে
from typing import Tuple # function thake return ar jonno

class Actions(IntEnum):
    up = 0
    down = 1
    left = 2
    right = 3
    up_right = 4
    up_left = 5
    down_right = 6
    down_left = 7

ACTION_TO_MOVE = {
    Actions.up : (-1, 0),
    Actions.down: (1, 0),
    Actions.left: (0, -1),
    Actions.right: (0, 1),
    Actions.up_right: (-1, 1),
    Actions.up_left: (-1, -1),
    Actions.down_right: (1, 1),
    Actions.down_left: (1, -1)
}

NUM_ACTION = len(Actions)

class DeliveryGridWorld:
    def __init__(self, n: int = 5, seed: int = 42) -> None:
        self.n = n
        self.rng = np.random.default_rng(seed)
        self.goal = (n-1, n-1)
        self.agent = None
        self.pickup = None
        self.carrying = False
        
    def _random_cell(self) -> Tuple[int,int]:
        row = int(self.rng.integers(self.n))
        col = int(self.rng.integers(self.n))
        
        # print(row, col)
        return (row, col)
    
    def reset(self):
        self.agent = self._random_cell()
        while True:
            candidate = self._random_cell()
            if candidate != self.goal and candidate != self.agent:
                self.pickup = candidate
                break
            
        self.carrying = False
        return self._get_state()
    
    def _get_state(self):
        agent_row, agent_col = self.agent
        pickup_row, pickup_col = self.pickup
        carrying_flag = int(self.carrying)
        
        return agent_row, agent_col, pickup_row, pickup_col, carrying_flag
    
    def step(self, action: int):
        done = False
        move_row, move_col = ACTION_TO_MOVE[Actions(action)]
        
        new_row = self.agent[0] + move_row
        new_col = self.agent[1] + move_col
        
        if 0 <= new_row < self.n and 0 <= new_col < self.n :
            self.agent = (new_row, new_col)
            reward = -1
            
            if self.agent == self.pickup and not self.carrying:
                self.carrying = True
                reward = 10
                
            if self.agent == self.goal and self.carrying:
                reward = 100
                done = True
                
        else: reward = -5
        return self._get_state(), reward, done
    
    def grid_print(self):

        for row in range(self.n):
            for col in range(self.n):

                if (row, col) == self.agent:
                    print("A", end=" ")

                elif (row, col) == self.pickup and not self.carrying:
                    print("P", end=" ")

                elif (row, col) == self.goal:
                    print("G", end=" ")

                else:
                    print(".", end=" ")

            print()
    
env = DeliveryGridWorld()
env.reset()

# env._random_cell()

done = False
step_count = 0
env.grid_print()

while not done and step_count < 600:
    step_count+=1
    action = np.random.randint(NUM_ACTION)
    next_state, reward, done = env.step(action)
    
    env.grid_print()
    
    print("Step count:", step_count)
    print("Action :", Actions(action).name)
    print("Reward :", reward)
    print("Carrying :", env.carrying)
    
    if done: break
    
    
# ======================================================
# 3. STATE → INDEX (Q-table row নির্ণয়)
# ======================================================

def state_to_index(state, n: int) -> int:
    
    agent_row, agent_col, pickup_row, pickup_col, carrying = state
    index = agent_row
    index = index * n + agent_col
    index = index * n + pickup_row
    index = index * n + pickup_col
    index = index * 2 + carrying_flag
    
    return index
    
    

# ======================================================
# 4. HELPERS: ε-greedy action + Q-update
# ======================================================

def choose_action(Q, state_index: int, epsilon: float, rng) -> int:

    if rng.random() < epsilon:
        return int(rng.integers(NUM_ACTIONS))   
    return int(np.argmax(Q[state_index]))          


def update_q_value(Q, state_index, action, reward, next_state_index, done, alpha, gamma):
    if done:
        best_future_value = 0.0
    else:
        best_future_value = np.max(Q[next_state_index])

    td_target = reward + gamma * best_future_value
    td_error = td_target - Q[state_index, action]
    Q[state_index, action] += alpha * td_error


