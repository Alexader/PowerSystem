import cvxpy as cp
import numpy as np
import json

# 读入电网结构的信息
with open("data.json", "r") as read_file:
    data = json.load(read_file)
nodeInfo = data["nodeInfo"]
lines = data["lineInfo"]

n = 5
m = 6
Nmax = 10
Nmin = -10
Umax = 1.05
Umin = 0.95
Imax = 1.95

np.random.seed(2)
R = np.zeros(n, n)	
X = np.zeros(n, n)
PLD = np.random.randn(n)
QLD = np.random.randn(n)
QCBStep = np.random.randn()
for line in lines:
	i = line["startNode"]
	j = line["endNode"]
	R[i][j] = R[j][i] = line["R"]
	X[i][j] = X[j][i] = line["X"]
for i, node in enumerate(nodeInfo):
	PLD[i] = node["PLD"]
	QLD[i] = node["QLD"]

Iij2 = cp.Variable(m)
U2 = cp.Variable(n)
PDG = cp.Variable(n) # J节点处的发电机功率
QSVG = cp.Variable(n)
QDG = cp.Variable(n)
QCB = cp.Variable(n)

Pij = cp.Variable(m) # 传输功率
Qij = cp.Variable(m)

P = cp.Variable(n) # 注入功率
Q = cp.Variable(n)
N_CB = cp.Variable(n, integer=True)


equal_constraints = []
inequal_constraints = []
# (4) (5) 号约束
adjacentTable = data["adjacentTable"]
for i in range(n):
    # 对于每一条线路都有潮流约束
    

# (6) 号等式约束
typeofNode = data["nodeType"] # 用字典保存节点的类型
for i in range(n):
    if typeofNode[i]==1: # 是发电机节点
        equal_constraints += [P[i] == PDG[i]-PLD[i]]
    else: # 负荷节点
        equal_constraints += [P[i] == PLD[i]]

#（7）号等式约束
for i in range(n):
	equal_constraints += [Q[i] == QDG[i] + QSVG[i] + QLD[i]]

#（8）号等式约束
def index2nodeNum(i, j):
    # i, j 号节点编号转化为支路标号
    return i*j
for i in range(n):
    for j in range(n):
        equal_constraints += [\
            U2[i] == U2[j] - 2*(R[i][j]*P[index2nodeNum(i,j)] + X[i][j]*index2nodeNum(i, j))\
            + (R[i][j]**2 + X[i][j]**2)*Iij2[index2nodeNum(i,j)]\
        ]
# (9) (10) 号约束
# node["hasCB"] 标记该节点是否配置容抗器
for i in range(n):
	if(nodeInfo["hasCB"] == True):
		inequal_constraints += [N_CB[i] <= Nmax, N_CB[i] >= Nmin]
		equal_constraints += [QCB[i] == N_CB[i]*QCBStep]
# (11) (12) 号约束
inequal_constraints += [U2 <= Umax, U2 >= Umin] # 电压约束
inequal_constraints += [Iij2 <= Imax] # 电流约束
# cone 约束
# We use cp.SOC(t, x) to create the SOC constraint ||x||_2 <= t.
cones = []
for i in range(m):
	# 每一条线路都是一个cone，X是长度为3的列向量，t是标量
	startNode = lines[i]["startNode"]
	cones.append(cp.SOC(Iij2[i]+U2[startNode],\
		[2*Pij[i], 2*Qij[i], Iij2[i]-U2[startNode]]))

obj = cp.Variable()
for i in range(m):
    obj += R[i]*Iij2[i]

objfn = cp.Minimize(obj)
prob = cp.Problem(objfn, equal_constraints+inequal_constraints+cones)
print(prob.is_dcp())