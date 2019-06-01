# --coding:utf-8 --
import cvxpy as cp
import numpy as np
import json
import math

# 读入电网结构的信息
with open("data.json", "r") as read_file:
    data = json.load(read_file)
nodeInfo = data["node"]
lines = data["lines"]

n = len(nodeInfo)
m = len(lines)

parentNode = [[] for j in range(n)]
childNode = [[] for j in range(n)]

# line :
#   0         1         2        3       4        5         6      7    8
# 线路编号 & 起始节点 & 结束节点 & {R_1} & {X_1} & {B_1/2} & {变比K}  Pij  Ploss
# 确定父子节点
R = np.zeros((n, n))
X = np.zeros((n, n))
for line in lines:
    i = line[1] - 1
    j = line[2] - 1
    R[i][j] = R[j][i] = line[3]
    X[i][j] = X[j][i] = line[4]
    if i != j:
        if line[7] > 0:
            parentNode[j] = i-1
            childNode[i] = j-1
        if line[7] < 0:
            parentNode[i] = j-1
            childNode[j] = i-1

PLD = []
QLD = []
U2 = []
PDG = []
QDG = []
QSVG = []
QCB = []
N_CB = []
Umax = 1.15
Umin = 0.9
Imax = 2
Pmax = 3
Qmax = 2.3

#  0     1      2         3        4       5      6       7       8     9   10      11
# 编号 &  U & {\theta} & {P_g} & {Q_g} & {P_L} & {Q_L} & 节点类型& SVG &  CB  NCB_max NCB_min
# 0 是平衡节点，1是PQ节点，2是 PV节点
# 确定变量集合
for node in nodeInfo:
    PLD.append(node[5])
    QLD.append(node[6])
    # 平衡节点是PQ不确定的节点
    if node[7] == 0:
        PDG.append(cp.Variable())
        QDG.append(cp.Variable())
        U2.append(cp.Variable())
    elif node[7] == 1: # PQ 节点的U不确定
        PDG.append(0.0)
        QDG.append(0.0)
        U2.append(cp.Variable())
    else: # PV节点的Q不确定
        QDG.append(cp.Variable())
        U2.append(node[1])
    # 根据装置的位置确定变量
    if node[8] == 1:
        QSVG.append(cp.Variable())
    else:
        QSVG.append(0.0)
    if node[9] == 1:
        QCB.append(cp.Variable())
        N_CB.append(cp.Variable(integer=True))
    else:
        QCB.append(0.0)
        N_CB.append(0.0)
# 运行优化
Iij2 = cp.Variable((n,n))
Pij = cp.Variable((n,n))
Qij = cp.Variable((n,n))
P = cp.Variable(n)
Q = cp.Variable(n)
equal_constraints = []
inequal_constraints = []
QCB_Step = 0.004

# 节点相关变量的约束
for node in nodeInfo:
    i = node[0] - 1
    equal_constraints += [P[i] == PDG[i] - PLD[i],
         Q[i] == QDG[i] +QSVG[i] + QCB[i] - QLD[i],
         QCB[i] == QCB_Step*N_CB[i]]
    if isinstance(QCB[i], cp.Variable):
        inequal_constraints += [N_CB[i] <= node[10], N_CB[i] >= node[11]]
    if isinstance(U2[i], cp.Variable):
        inequal_constraints += [U2[i] <= Umax, U2[i] >= Umin]
    if isinstance(P[i], cp.Variable):
        inequal_constraints += [P[i] <= Pmax, P[i] >= 0]
    if isinstance(Q[i], cp.Variable):
        inequal_constraints += [Q[i] <= Qmax]
# 支路相关变量的约束
LineExist = {}
for line in lines:
    i = line[1] - 1
    j = line[2] - 1
    if i != j:
        equal_constraints += [
            U2[i] - U2[j] == 2*(R[i][j]*Pij[i][j] + X[i][j]*Q[i][j]) - Iij2[i][j]*(R[i][j]**2 + X[i][j]**2),
            U2[j] - U2[i] == 2*(R[i][j]*Pij[j][i] + X[i][j]*Q[j][i]) - Iij2[j][i]*(R[i][j]**2 + X[i][j]**2)
        ]
        LineExist[(i, j)] = LineExist[(j, i)] = 1
# 变量替换中自然带有的约束
for i in range(n):
    for j in range(i+1, n):
        inequal_constraints += [Pij[i][j] + Pij[j][i] >= 0]
        equal_constraints += [Iij2[i][j] == Iij2[j][i],
                            Qij[i][j] == Qij[j][i],
                            Iij2[i][j]*R[i][j] == Pij[i][j] + Pij[j][i]]
        if (i, j) not in LineExist:
            equal_constraints += [Iij2[i][j] == 0]
        
for node in nodeInfo:
    i = node[0] - 1
    sumParentP = sumParentQ = 0
    sumChildP = sumChildQ = 0
    for parent in parentNode[i]:
        sumParentP += (Pij[parent][i] - Iij2[parent][i]*R[parent][i])
        sumParentQ += (Qij[parent][i] - Iij2[parent][i]*X[parent][i])
    for child in childNode[i]:
        sumChildP += (P[i][child] - Iij2[i][child]*R[i][child])
        sumChildQ += (Q[i][child] - Iij2[i][child]*X[i][child])
    equal_constraints += [sumParentP + P[i] == sumChildP,\
                        sumParentQ + Q[i] == sumChildQ]
equal_constraints += [Iij2 <= Imax, Iij2 >= 0]

# cone 相关的约束
cones = []
for line in lines:
    i = line[1] - 1
    j = line[2] - 1
    Xcone = cp.vstack(2*Pij[i][j], 2*Qij[i][j], Iij2[i][j] - U2[i])
    t = Iij2[i][j] + U2[i]
    cones += [cp.SOC(t, Xcone)]
obj = 0
for line in lines:
    i = line[1] - 1
    j = line[2] - 1
    obj += R[i][j]*Iij2[i][j]

prob = cp.Problem(cp.Minimize(obj), equal_constraints + inequal_constraints + cones)
prob.solve(solver=cp.CVXOPT)
print(prob.status)
print(prob.value)
# 产生优化后的数据

# 分析优化后的数据
