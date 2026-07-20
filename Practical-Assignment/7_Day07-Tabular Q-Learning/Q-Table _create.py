import numpy as np


class GridWorld:
    def __init__(self, grid_size=5, holes=None):
        self.grid_size = grid_size
        self.holes = holes if holes is not None else []
        self.B = (grid_size - 1, grid_size - 1)
        self.n_actions = 4                                # Up, Down, Left, Right
        self.n_states = grid_size * grid_size * 2         # row × col × carrying
        self.reset()

    def reset(self):
        # ... তোমার আগের reset code (অপরিবর্তিত) ...
        while True:
            r, c = np.random.randint(0, self.grid_size, size=2)
            if (r, c) != self.B:
                self.agent_row, self.agent_col = int(r), int(c)
                break
        while True:
            r, c = np.random.randint(0, self.grid_size, size=2)
            if (r, c) != self.B and (r, c) != (self.agent_row, self.agent_col):
                self.A = (int(r), int(c))
                break
        self.carrying = False
        self.done = False
        return self._get_state()

    def _get_state(self):
        return (self.agent_row, self.agent_col, self.carrying)

    def state_to_index(self, state):
        row, col, carrying = state
        return row * (self.grid_size * 2) + col * 2 + int(carrying)


env = GridWorld(grid_size=5)
Q = np.zeros((env.n_states, env.n_actions))

print("Q-Table shape:", Q.shape)
print("Total cells  :", Q.size)
print(Q[:5])

# Test: state_to_index সঠিকভাবে কাজ করছে কিনা
test_states = [
    (0, 0, False),
    (0, 0, True),
    (0, 1, False),
    (4, 4, False),
    (4, 4, True),
]

for s in test_states:
    idx = env.state_to_index(s)
    print(f"State {s} → index {idx}")
