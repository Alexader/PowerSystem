import cvxpy as cp
import numpy as np
import json

# 读入电网结构的信息
with open("powerFlow.json", "r") as read_file:
    data = json.load(read_file)
nodeInfo = data["node"]
lines = data["lines"]

n = len(nodeInfo)
m = len(lines)
Nmax = 10
Nmin = -10
Umax = 1.05
Umin = 0.95
Imax = 1.95

R = np.zeros(n, n)
X = np.zeros(n, n)
PLD = []
QLD = []
# 按照节点的类型进行分类，从而可以区分不同的变量
# [平衡节点， PV节点， PQ节点]
U2 = []
PDG = []
QDG = []
QSVG = [] # 节点处的SVG提供的无功调节，没有安装则为0
QCB = [] # 同上
N_CB = []
# 记录负荷功率值
for item in nodeInfo:
    # item 为list类型
    #  0     1      2         3        4       5      6       7       8     9   10
    # 编号 &  U & {\theta} & {P_g} & {Q_g} & {P_L} & {Q_L} & 节点类型& SVG &  CB  
    # 0 是平衡节点，1是PQ节点，2是 PV节点
    PLD.append(item[4])
    QLD.append(item[5])
    # 判断是否有可调发电机
    if item[7]==1:
        U2.append(cp.Variable())
        PDG.append(cp.Variable())
        QDG.append(cp.Variable())
    else:
        U2.append(1.0)
        PDG.append(0.0)
        PDG.append(0.0)
    # 判断是否有安装 SVG 和 CB装置
    if item[8] == 0:
        QSVG.append(0.0)
    else :
        QSVG.append(cp.Variable())
    if item[9] == 0:
        QCB.append(0.0)
        N_CB.append(0.0)
    else:
        QCB.append(cp.Variable())
        N_CB.append(cp.Variable(1, integer=True))

QCBStep = np.random.randn()
for line in lines:
    # lines 为 矩阵形式的 list
    # line :
    #   0         1         2        3       4        5         6
    # 线路编号 & 起始节点 & 结束节点 & {R_1} & {X_1} & {B_1/2} & {变比K}
	i = line[1]
	j = line[2]
	R[i][j] = R[j][i] = line[3]
	X[i][j] = X[j][i] = line[4]

Iij2 = cp.Variable(m)

Pij = cp.Variable(m) # 传输功率
Qij = cp.Variable(m)

P = cp.Variable(n) # 注入功率
Q = cp.Variable(n)

equal_constraints = []
inequal_constraints = []
# (4) (5) 号约束
adjacentTable = data["adjacentTable"]
for i in range(n):
    # 对于每一条线路都有潮流约束
    ...

# (6) 号等式约束
for i in range(n):
    if nodeInfo[i][7]==1: # 是发电机节点
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
    for j in range(i+1, n):
        equal_constraints += [\
            U2[i] == U2[j] - 2*(R[i][j]*P[index2nodeNum(i,j)] + X[i][j]*index2nodeNum(i, j))\
            + (R[i][j]**2 + X[i][j]**2)*Iij2[index2nodeNum(i,j)]\
        ]
# (9) (10) 号约束
# nodeInfo[i][9] 标记该节点是否配置容抗器
for i in range(n):
	if(nodeInfo[i][9] == 1):
		inequal_constraints += [N_CB[i] <= Nmax, N_CB[i] >= Nmin]
		equal_constraints += [QCB[i] == N_CB[i]*QCBStep]
# (11) (12) 号约束
for i in range(n):
    if nodeInfo[7] == 1:
        inequal_constraints += [U2[i] <= Umax, U2[i] >= Umin] # 电压约束
inequal_constraints += [Iij2 <= Imax] # 电流约束
# cone 约束
# We use cp.SOC(t, x) to create the SOC constraint ||x||_2 <= t.
cones = []
for i in range(m):
	# 每一条线路都是一个cone，X是长度为3的列向量，t是标量
	startNode = lines[i][1]
	cones.append(cp.SOC(Iij2[i]+U2[startNode],\
		[2*Pij[i], 2*Qij[i], Iij2[i]-U2[startNode]]))

obj = cp.Variable()
for k in range(m):
    i = lines[k][1]
    j = lines[k][2]
    obj += R[i][j]*Iij2[k]

objfn = cp.Minimize(obj)
prob = cp.Problem(objfn, equal_constraints+inequal_constraints+cones)
print(prob.is_dcp())
