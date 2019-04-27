import cvxpy as cp
import numpy as np


n = 5
m = 6
# VN = cp.Constant(n)
# QN = cp.Constant(m)
# Vmax = np.full(n, 1.05)
# # Vmax = cp.Constant(Vmax)
# Vmin = np.full(n, 0.95)
# Qmax = np.full(m, 1.05)
# Qmin = np.full(m, 0.95)
# DeltaV = cp.Variable(n)
# DeltaQ = cp.Variable(m)
# Y = cp.Constant((n,n))

# DeltaP = 
# objfn = cp.Minimize(cp.sum(DeltaV**2) + cp.sum(DeltaQ**2))
# constraints = [DeltaV + VN <= Vmax, DeltaV + VN >= Vmin, DeltaQ + QN <= Qmax, DeltaQ + QN >= Qmin]

# prob = cp.Problem(objfn, constraints)
# print(prob.is_dcp())
# prob.solve()
# print(prob.value)

Iij2 = cp.Variable(m)
U2 = cp.Variable(n)
R = np.random.randn(n, n)
X = np.random.randn(n, n)
PLD = np.random.randn(n)
PJD = cp.Variable(n)
Pij = cp.Variable(m) # 传输功率
Qij = cp.Variable(m)
P = cp.Variable(n) # 注入功率
Q = cp.Variable(n)
N_CB = cp.Variable(n, integer=True)


equal_constraints = []
for i in range(m):
    # 对于每一条线路都有潮流约束
    for j in range(m):
        a = i*j

# (6) 号等式约束
typeofNode = {} # 用字典保存节点的类型
for i in range(n):
    if typeofNode[i]==1: # 是发电机节点
        equal_constraints += [P[i] == PJD[i]-PLD[i]]
    else: # 负荷节点
        equal_constraints += [P[i] == PLD[i]]

#（7）号等式约束
for i in range(n):
	QiDG = 
# （8）号等式约束
def index2nodeNum(i, j):
    # i, j 号节点编号转化为支路标号
    return i*j
for i in range(n):
    for j in range(n):
        equal_constraints += [\
            U2[i] == U2[j] - 2*(R[i][j]*P[index2nodeNum(i,j)] + X[i][j]*index2nodeNum(i, j))\
            + (R[i][j]**2 + X[i][j]**2)*Iij2[index2nodeNum(i,j)]\
        ]

obj = cp.Variable()
for i in range(m):
    obj += R[i]*Iij2[i]

objfn = cp.Minimize(obj)
