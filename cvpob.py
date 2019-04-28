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
Nmax = 10
Nmin = -10
Umax = 1.05
Umin = 0.95
Imax = 1.95

Iij2 = cp.Variable(m)
U2 = cp.Variable(n)
np.random.seed(2)
R = np.random.randn(n, n)
X = np.random.randn(n, n)
PLD = np.random.randn(n)
QLD = np.random.randn(n)
QCBStep = np.random.randn()


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
for i in range(m):
    # 对于每一条线路都有潮流约束
    for j in range(m):
        a = i*j

# (6) 号等式约束
typeofNode = {} # 用字典保存节点的类型
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
hasCapBank = np.random.randn(n) # 标记该节点是否配置容抗器
for i in range(n):
	if(hasCapBank[i] == True):
		inequal_constraints += [N_CB[i] <= Nmax, N_CB[i] >= Nmin]
		equal_constraints += [QCB[i] == N_CB[i]*QCBStep]
# (11) (12) 号约束
inequal_constraints += [U2 <= Umax, U2 >= Umin] # 电压约束
inequal_constraints += [Iij2 <= Imax] # 电流约束
# cone 约束
# We use cp.SOC(t, x) to create the SOC constraint ||x||_2 <= t.
X_cone = [2*Pij, 2*Qij, Iij2 - U2]
cone_constraints = cp.SOC(X_cone, Iij2 + U2)
obj = cp.Variable()
for i in range(m):
    obj += R[i]*Iij2[i]

objfn = cp.Minimize(obj)
prob = cp.Problem(objfn, equal_constraints+inequal_constraints)
print(prob.is_dcp())