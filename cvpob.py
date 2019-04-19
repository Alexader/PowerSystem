import cvxpy as cp
import numpy as np


n = 5
m = 6
VN = cp.Constant(n)
QN = cp.Constant(m)
Vmax = np.full(n, 1.05)
# Vmax = cp.Constant(Vmax)
Vmin = np.full(n, 0.95)
Qmax = np.full(m, 1.05)
Qmin = np.full(m, 0.95)
DeltaV = cp.Variable(n)
DeltaQ = cp.Variable(m)
Y = cp.Constant((n,n))

DeltaP = 
objfn = cp.Minimize(cp.sum(DeltaV**2) + cp.sum(DeltaQ**2))
constraints = [DeltaV + VN <= Vmax, DeltaV + VN >= Vmin, DeltaQ + QN <= Qmax, DeltaQ + QN >= Qmin]

prob = cp.Problem(objfn, constraints)
print(prob.is_dcp())
prob.solve()
print(prob.value)
