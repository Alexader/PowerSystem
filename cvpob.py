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
Nmax = 10
Nmin = -10
Umax = 1.05
Umin = 0.95
Imax = 1.95

R = np.zeros((n, n))
X = np.zeros((n, n))
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
# 构造电网结构的邻接矩阵
Graph = [[] for i in range(n)]
parentNode = [[] for j in range(n)]
childNode = [[] for j in range(n)]

nodeNum2LineNum = {}
for line in lines:
    i = line[1]
    j = line[2]
    if i != j:
        nodeNum2LineNum[(i, j)] = nodeNum2LineNum[(j, i)] = line[0]
        Graph[i-1].append(j)
        Graph[j-1].append(i)
        if line[7] > 0:# 判断潮流的流向
            parentNode[j-1].append(i)
            childNode[i-1].append(j)
        else:
            parentNode[i-1].append(j)
            childNode[j-1].append(i)
    else :
        nodeInfo[i][9] = 1

# 记录负荷功率值
for item in nodeInfo:
    # item 为list类型
    #  0     1      2         3        4       5      6       7       8     9   10
    # 编号 &  U & {\theta} & {P_g} & {Q_g} & {P_L} & {Q_L} & 节点类型& SVG &  CB  
    # 0 是平衡节点，1是PQ节点，2是 PV节点
    PLD.append(item[5])
    QLD.append(item[6])
    # 判断是否有可调发电机
    if item[7]==2:
        U2.append(1.1)
        PDG.append(cp.Variable())
        QDG.append(cp.Variable())
    else:
        U2.append(cp.Variable())
        PDG.append(0.0)
        QDG.append(0.0)
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
        N_CB.append(cp.Variable(integer=True))

QCBStep = 0.01
for line in lines:
    # lines 为 矩阵形式的 list
    # line :
    #   0         1         2        3       4        5         6      7
    # 线路编号 & 起始节点 & 结束节点 & {R_1} & {X_1} & {B_1/2} & {变比K}  Pij
	i = line[1]-1
	j = line[2]-1
	R[i][j] = R[j][i] = line[3]
	X[i][j] = X[j][i] = line[4]

Iij2 = cp.Variable((n, n))

Pij = cp.Variable((n, n)) # 传输功率
Qij = cp.Variable((n,n))
Y = cp.Variable(shape=(3, m))
Z = cp.Variable(m)

P = cp.Variable(n) # 注入功率
Q = cp.Variable(n)

equal_constraints = []
inequal_constraints = []
# 矩阵必须是对称矩阵
for i in range(n):
	for j in range(n):
		equal_constraints += [Iij2[i][j] == Iij2[j][i]]
# 传输功率限制
for line in lines:
	i = line[1] - 1
	j = line[2] - 1
	equal_constraints += [(Pij[i][j]+Pij[j][i]) == Iij2[i][j]*R[i][j]]
# (4) (5) 号约束
# 对于每一个节点计算支路潮流等式
for i in range(n):
    sumParentP = sumParentQ = 0
    sumChildP = sumChildQ = 0
    for parent in parentNode[i]:
        sumParentP += (Pij[parent-1][i] - Iij2[parent-1][i]*R[parent-1][i])
        sumParentQ += (Qij[parent-1][i] - Iij2[parent-1][i]*X[parent-1][i])
    for child in childNode[i]:
        sumChildP += Pij[i][child - 1]
        sumChildQ += Qij[i][child - 1]
    equal_constraints += [sumParentP + P[i] == sumChildP, sumParentQ + Q[i] == sumChildQ]

# (6) 号等式约束
for i in range(n):
    # if nodeInfo[i][7]==1: # 负荷节点
    #     equal_constraints += [P[i] == -PLD[i]]
    # else: # 是发电机节点
    #     equal_constraints += [P[i] == PDG[i]-PLD[i]]
    equal_constraints += [P[i] == PDG[i] - PLD[i]]

#（7）号等式约束
print(len(PLD))
for i in range(n):
	equal_constraints += [Q[i] == QDG[i] + QSVG[i] +QCB[i] - QLD[i]]

#（8）号等式约束
for line in lines:
	#   0         1         2        3       4        5         6      7
    # 线路编号 & 起始节点 & 结束节点 & {R_1} & {X_1} & {B_1/2} & {变比K} & Pij
    i = line[1]-1
    j = line[2]-1
    equal_constraints += [
        U2[i] == U2[j] - 2*(R[i][j]*Pij[i][j] + X[i][j]*Qij[i][j])\
        + (R[i][j]**2 + X[i][j]**2)*Iij2[i][j],\
		U2[j] == U2[i] - 2*(R[i][j]*Pij[j][i] + X[i][j]*Qij[j][i])\
		+ (R[i][j]**2 + X[i][j]**2)*Iij2[j][i]
    ]
# (9) (10) 号约束
# nodeInfo[i][9] 标记该节点是否配置容抗器
for i in range(n):
	if(nodeInfo[i][9] == 1):
		inequal_constraints += [N_CB[i] <= Nmax, N_CB[i] >= Nmin]
		equal_constraints += [QCB[i] == N_CB[i]*QCBStep]
# (11) (12) 号约束
for i in range(n):
    if nodeInfo[i][7] == 1:
        inequal_constraints += [U2[i] <= Umax, U2[i] >= Umin] # 电压约束
inequal_constraints += [Iij2 <= Imax, Iij2 >= 0] # 电流约束
# cone 约束
# We use cp.SOC(t, x) to create the SOC constraint ||x||_2 <= t.
#	|| 2*Pij  ||
#	|| 2*Qij  ||  <= I2ij+U2i
#	|| I2ij-U2i ||2
#   进行变量替换和合并，需要增加下面新的约束
#	Y[0] = 2*Pij, Y[1] = 2*Qij, Y[2] = I2ij-U2i
#	Z = I2ij+U2i
cones = []
for line in lines:
	# 每一条线路都是一个cone，X是长度为3的列向量，t是标量
	i = line[1] - 1
	j = line[2] - 1
	equal_constraints += [
		Y[0][i] == 2*Pij[i][j], 
		Y[1][i] == 2*Qij[i][j], 
		Y[2][i] == Iij2[i][j]-U2[i-1],
		Z[i] == Iij2[i][j] + U2[i - 1],
		Y[2][i] + Z[i] == 2*Iij2[i][j],
		Z[i] - Y[2][i] == 2*U2[i-1]
	]

cones += [cp.SOC(Z, Y)]
obj = 0
for k in range(m):
    i = lines[k][1]-1
    j = lines[k][2]-1
    obj += R[i][j]*Iij2[i][j]

objfn = cp.Minimize(obj)
prob = cp.Problem(objfn, equal_constraints+inequal_constraints+cones)
# print(prob.is_mixed_integer())

value = prob.solve(solver=cp.ECOS_BB)

#输出优化后的结果
for i, voltage in enumerate(U2):
    if isinstance(voltage, cp.Variable):
        print("the voltage of node {} is {}".format(i+1, math.sqrt(voltage.value)))
    else :
        print("const votage value of node {} is {}".format(i+1, voltage))
for line in lines:
	i = line[1]
	j = line[2]
	print("current vlaue of line {} to {} is {}".format(i, j, Iij2[i-1][j-1].value))
for i, item in enumerate(N_CB):
    if isinstance(item, cp.Variable):
        print("Capacitor at node {} is in {}".format(i+1, item.value))
for i in range(n):
	for j in range(n):
		print("S[{}][{}] is {}".format(i+1, j+1, Pij[i][j].value))
		# print("current of node {} to node {} is {}".format(i+1, j+1, math.sqrt(Iij2[i][j].value)))
print(prob.value)
print(prob.status)