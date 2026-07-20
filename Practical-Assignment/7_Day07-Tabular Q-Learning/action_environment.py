# python Library
import numpy as np
import matplotlib.pyplot as plt
from enum import IntEnum
from typing import Tuple

# ==========================================
# 1. ACTIONS: 8টি দিক (4 সোজা + 4 কোনাকুনি)
# ==========================================

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

# ======================================================
# 2. ENVIRONMENT: n×n grid world
# Agent, Pickup, Goal কোথায় আছে?
# Move করলে কী হবে? Reward কত হবে? Episode শেষ হবে কিনা?
# ======================================================

class DeliveryGridWorld:
    def __init__(self, n: int = 5, seed: int = 42) -> None:
        self.n = n
        self.rng = np.random.default_rng(seed)
        self.goal = (n-1, n-1)
        
        # এই তিনটি field reset()-এ initialise হবে
        self.agent = None
        self.pickup = None
        self.carrying = False
        
    def _random_cell(self) -> Tuple[int,int]:
        row = int(self.rng.integers(self.n))
        col = int(self.rng.integers(self.n))
    
        # print((row, col))
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
    
    def step(self, action : int):
        done = False
        move_row, move_col = ACTION_TO_MOVE[Actions(action)]
        
        new_row = self.agent[0] + move_row
        new_col = self.agent[1] + move_col
        
        if 0 <= new_row < self.n and 0 <= new_col < self.n:
            self.agent = (new_row, new_col)
            reward = -1
            
            if self.agent == self.pickup and not self.carrying:
                self.carrying = True
                reward = 10
                
            if self.agent == self.goal and self.carrying:
                reward = 100
                done = True
        
        else : reward = -5
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
state = env.reset()

done = False
step_count = 0

print("Initial Grid")
env.grid_print()
while not done and step_count < 500:
    action = np.random.randint(NUM_ACTION)
    next_state, reward, done = env.step(action)
    step_count += 1
    
    print("----------------")
    print("Step :", step_count)
    print("Action :", Actions(action).name)
    print("Reward :", reward)
    print("Carrying :", env.carrying)

    env.grid_print()
    
    if done: break
