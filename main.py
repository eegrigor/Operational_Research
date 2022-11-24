import gurobipy as gp
from gurobipy import GRB
import itertools as it

#first problem
print("Solving first problem \n")

#how many states we have
n = [1, 2, 3, 4, 5]

#we find all the color transitions
transitions  = list(it.permutations(n))

#mixing times
mix_time = [20, 35, 45, 32, 50]

#cleaning time table
cleaning = [[0, 11, 7, 13, 11],
            [5, 0, 13, 15, 15],
            [13, 15, 0, 23, 11],
            [9, 13, 5, 0, 3],
            [3, 7, 7, 7, 0]]

transition_table = [[0 for i in range(len(mix_time)+1)] for j in range(len(transitions))]

# find all possible combinations
for i in range(len(transitions)):
    for j in range(len(mix_time)+1):
        if j != len(mix_time):
            transition_table[i][j] = transitions[i][j] - 1
        else:
            transition_table[i][j] = transition_table[i][0]

m1 = gp.Model("Problem1")
X1 = {}
opt1 ={}
for i in range(len(transition_table)):
    for j in range(len(mix_time)+1):
        X1[i,j] = m1.addVar(vtype=GRB.BINARY)

for i in range(len(transition_table)):
    opt1[i] = m1.addVar()
for i in range(len(transition_table)):
        m1.addConstr((opt1[i] ==1) >> (X1[i,0] + X1[i,1] + X1[i,2] + X1[i,3] +X1[i,4] +X1[i,5] == 6),"C1")

#make sure that only one of the above constraints is true
m1.addConstr(gp.quicksum(opt1[i] for i in range(len(transition_table))) == 1,"C2")

m1.setObjective(gp.quicksum((X1[i,j] * cleaning[transition_table[i][j]][transition_table[i][j+1]])  for i in range(len(transition_table)) for j in range(len(mix_time))) + 202, GRB.MINIMIZE)

m1.optimize()

#prints all variables values
# for v in m1.getVars():
#     print(str(v.VarName)+"="+str(round(v.x,2)))

#prints the non zeros variables
# m1.printAttr('x')
# looking at which variables are 1 we find that the line we want is line 68
# +1 is added because we have subtracted 1 at the intiallization(line 30)
print("The optimal sequence is ",transition_table[68][0] +1, transition_table [68][1]+1 , transition_table [68][2]+1, transition_table [68][3]+1,transition_table [68][4]+1)

#Second problem
print("\n Solving second problem \n")

#number of "Tap"
tap = (1,2,3)

#number of machines
machines = (1,2,3)

#sequence of machines for each "Tap"
sequence = {1:[1,3],2:[2,1,3],3:[3,1,2]}

#time for each "Tap" in one machine
time = {(1,1): 45,
        (1,3): 10,
        (2,2): 10,
        (2,1): 20,
        (2,3): 34,
        (3,3): 28,
        (3,1): 12,
        (3,2): 17}

#table it is used for easier initialization of model variables
table = [(i,j) for i in tap for j in sequence[i]]

m2 = gp.Model("Problem2")
# x[i,j]--> time that tapi starts in machine j
x2 = m2.addVars(table,vtype=GRB.INTEGER,name ='x2')
opt2 = m2.addVars(table,vtype=GRB.BINARY,name='opt')
y = m2.addVar(vtype=GRB.INTEGER,name = 'y')

#constraints for tap1
m2.addConstr(x2[1,1] + time[1,1] <= x2[1,3])

#constrains for tap2
m2.addConstr(x2[2,2] + time[2,2] <= x2[2,1])
m2.addConstr(x2[2,1] + time[2,1] <= x2[2,3])

#constraints for tap3
m2.addConstr(x2[3,3] + time[3,3] <= x2[3,1])
m2.addConstr(x2[3,1] + time[3,1] <= x2[3,2])

#constraints for machine1
m2.addConstr((opt2[1,1] == 1) >> ((x2[1,1] + time[1,1] <= x2[2,1])))
m2.addConstr((opt2[1,1] == 1) >> ((x2[1,1] + time[1,1] <= x2[3,1])))
m2.addConstr((opt2[2,1] == 1) >> ((x2[2,1] + time[2,1] <= x2[1,1])))
m2.addConstr((opt2[2,1] == 1) >> ((x2[2,1] + time[2,1] <= x2[3,1])))
m2.addConstr((opt2[3,1] == 1) >> ((x2[3,1] + time[3,1] <= x2[1,1])))
m2.addConstr((opt2[3,1] == 1) >> ((x2[3,1] + time[3,1] <= x2[2,1])))
m2.addConstr(opt2[1,1] + opt2[2,1] + opt2[3,1] == 1)

#constraints for machine2
m2.addConstr((opt2[2,2] == 1) >> ((x2[2,2] + time[2,2] <= x2[3,2])))
m2.addConstr((opt2[3,2] == 1) >> ((x2[3,2] + time[3,2] <= x2[2,2])))
m2.addConstr(opt2[2,2] + opt2[3,2] == 1)

#constraints for machine3
m2.addConstr((opt2[1,3] == 1) >> ((x2[1,3] + time[1,3] <= x2[2,3])))
m2.addConstr((opt2[1,3] == 1) >> ((x2[1,3] + time[1,3] <= x2[3,3])))
m2.addConstr((opt2[2,3] == 1) >> ((x2[2,3] + time[2,3] <= x2[1,3]) ))
m2.addConstr((opt2[2,3] == 1) >> ((x2[2,3] + time[2,3] <= x2[3,3]) ))
m2.addConstr((opt2[3,3] == 1) >> ((x2[3,3] + time[3,3] <= x2[1,3])))
m2.addConstr((opt2[3,3] == 1) >> ((x2[3,3] + time[3,3] <= x2[2,3])))
m2.addConstr(opt2[1,3] + opt2[2,3] + opt2[3,3] == 1)

#total time constraint
m2.addConstr(y >= x2[1,3] + time[1,3])
m2.addConstr(y >= x2[2,3] + time[2,3])
m2.addConstr(y >= x2[3,2] + time[3,2])

m2.setObjective(y,GRB.MINIMIZE)

m2.optimize()

# print variables values
for v in m2.getVars():
    print(str(v.VarName)+"="+str(round(v.x,2)))