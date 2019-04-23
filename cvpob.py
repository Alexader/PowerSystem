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
Pij = cp.Variable(m) # 传输功率
Qij = cp.Variable(m)
P = cp.Variable(n) # 注入功率
Q = cp.Variable(n)
equal_constraints = []
for i in range(m):
    # 对于每一条线路都有潮流约束
    for j in range(m):
obj = cp.Variable()

objfn = cp.Minimize(obj)
