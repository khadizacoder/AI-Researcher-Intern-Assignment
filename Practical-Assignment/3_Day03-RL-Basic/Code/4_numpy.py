import numpy as np

num_states = 25
action = 8

q_table = np.zeros((num_states, action))
# print(q_table.shape) # ২৫টি Row (State) ৮টি Column (Action)

# Q = np.zeros((3,4))
# print(Q)

# p = np.zeros((3,5)) # Float value
p = np.zeros((3,5), dtype=int) #integer value
p[0][1] = 5
p[2][2] = 10
print(p)

print('new table')

a = np.zeros((3,3), dtype=int)

a[0][0] = 1
a[1][1] = 2
a[2][2] = 3

print(a)