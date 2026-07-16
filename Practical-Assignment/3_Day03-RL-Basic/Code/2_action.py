import random
actions = [
    'Up',
    'Down',
    'Left',
    "Right",
    "UpLeft",
    "UpRight",
    "DownLeft",
    "DownRight"
]

# print(actions[0])
# print(actions[6])

# for action in actions:
#     print(action)

move = random.choice(actions)
print(move)