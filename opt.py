# --coding:utf-8 --
import cvxpy as cp
import numpy as np
import json
import math
import datetime

start = datetime.datetime.now()
# 读入电网结构的信息
with open("data.json", "r") as read_file:
    data = json.load(read_file)
nodeInfo = data["node"]
lines = data["lines"]

n = len(nodeInfo)
m = len(lines)
print(n)

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
            parentNode[j].append(i-1)
            childNode[i].append(j-1)
        if line[7] < 0:
            parentNode[i].append(j-1)
            childNode[j].append(i-1)

PLD = []
QLD = []
U2 = []
PDG = []
QDG = []
QSVG = []
QCB = []
N_CB = []
Umax = 1.05
Umin = 0.95
Imax = 2
Pmax = 8
Qmax = 1.5

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
        PDG.append(node[3])
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
# P = cp.Variable(n)
# Q = cp.Variable(n)
Y = cp.Variable(shape=(3, m))
Z = cp.Variable(m)
equal_constraints = []
inequal_constraints = []
QCB_Step = 0.004

# 节点相关变量的约束
for node in nodeInfo:
    i = node[0] - 1
    # equal_constraints += [P[i] == PDG[i] - PLD[i],
    #      Q[i] == QDG[i] +QSVG[i] + QCB[i] - QLD[i]
    #      ]
    if isinstance(QCB[i], cp.Variable):
        equal_constraints += [QCB[i] == QCB_Step*N_CB[i]]
        inequal_constraints += [N_CB[i] <= node[10], N_CB[i] >= node[11]]
    if isinstance(U2[i], cp.Variable):
        inequal_constraints += [U2[i] <= Umax, U2[i] >= Umin]
    if isinstance(QSVG[i], cp.Variable):
        inequal_constraints += [QSVG[i] <= Qmax, QSVG[i] >= 0]
    # if isinstance(P[i], cp.Variable):
    #     inequal_constraints += [P[i] <= Pmax, P[i] >= 0]
    # if isinstance(Q[i], cp.Variable):
    #     inequal_constraints += [Q[i] <= Qmax]
# 支路相关变量的约束
LineExist = {}
for line in lines:
    i = line[1] - 1
    j = line[2] - 1
    if i != j:
        equal_constraints += [
            U2[i] - U2[j] == 2*(R[i][j]*Pij[i][j] + X[i][j]*Qij[i][j]) - Iij2[i][j]*(R[i][j]**2 + X[i][j]**2),
            U2[j] - U2[i] == 2*(R[i][j]*Pij[j][i] + X[i][j]*Qij[j][i]) - Iij2[j][i]*(R[i][j]**2 + X[i][j]**2)
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
                # Pij[i][j] == 0, Pij[j][i] == 0,
                # Qij[i][j] == 0, Qij[j][i] == 0]
        
for node in nodeInfo:
    i = node[0] - 1
    sumParentP = sumParentQ = 0
    sumChildP = sumChildQ = 0
    for parent in parentNode[i]:
        sumParentP += (Pij[parent][i] - Iij2[parent][i]*R[parent][i])
        sumParentQ += (Qij[parent][i] - Iij2[parent][i]*X[parent][i])
    for child in childNode[i]:
        sumChildP += (Pij[i][child] - Iij2[i][child]*R[i][child])
        sumChildQ += (Qij[i][child] - Iij2[i][child]*X[i][child])
    if type(sumParentP + PDG[i] - PLD[i] == sumChildP) != bool:
        equal_constraints += [sumParentP + PDG[i] - PLD[i] == sumChildP]
    if type(sumParentQ + QDG[i] + QSVG[i] + QCB[i] == sumChildQ + QLD[i]) != bool:
        equal_constraints += [sumParentQ + QDG[i] + QSVG[i] + QCB[i] == sumChildQ + QLD[i]]
equal_constraints += [Iij2 <= Imax, Iij2 >= 0]

# cone 相关的约束
cones = []
for line in lines:
    i = line[1] - 1
    j = line[2] - 1
    Xcone = cp.vstack((2*Pij[i][j], 2*Qij[i][j], Iij2[i][j] - U2[i]))
    t = Iij2[i][j] + U2[i]
    cones += [cp.SOC(t, Xcone)]
#     equal_constraints += [
# 		Y[0][i] == 2*Pij[i][j], 
# 		Y[1][i] == 2*Qij[i][j], 
# 		Y[2][i] == Iij2[i][j]-U2[i-1],
# 		Z[i] == Iij2[i][j] + U2[i - 1],
# 		Y[2][i] + Z[i] == 2*Iij2[i][j],
# 		Z[i] - Y[2][i] == 2*U2[i-1]
# 	]
# cones += [cp.SOC(Z, Y)]
sumQ = 0
for i in range(n):
    if nodeInfo[i][7] == 2:
        sumQ += QDG[i]
    if nodeInfo[i][8] == 1:
        sumQ += QSVG[i]
    if nodeInfo[i][9] == 1:
        sumQ += QCB[i]
equal_constraints += [sumQ == sum(QLD)]
obj = 0
for line in lines:
    i = line[1] - 1
    j = line[2] - 1
    obj += R[i][j]*Iij2[i][j]

prob = cp.Problem(cp.Minimize(obj), equal_constraints + inequal_constraints + cones)
prob.solve(solver=cp.ECOS_BB)
print(prob.status)
print(prob.value)

loss = 0.885888744
optimal = 0
for line in lines:
    i = line[1] - 1
    j = line[2] - 1
    optimal += Pij[i][j].value+Pij[j][i].value
print("loss reduce by {}% in prob.value".format((loss - prob.value)/loss*100))
print("loss reduce by {}% in optimal".format((loss - optimal)/loss))

# 分析优化后的数据
end = datetime.datetime.now()
print("程序耗时：{} S".format(end - start))
# 产生优化后的数据
import xlsxwriter
wbk = xlsxwriter.Workbook("潮流.xlsx")
Ust = wbk.add_worksheet("U")
Ust.write(0, 0, "编号")
Ust.write(0, 1, "电压幅值")
Ust.write(0, 2, "QSVG")
Ust.write(0, 3, "QCB")
Ust.write(0, 4, "PDG")
Ust.write(0, 5, "QDG")
Ust.write(0, 6, "PLD")
Ust.write(0, 7, "QLD")
Ust.write(0, 8, "P")
Ust.write(0, 9, "Q")
for i, voltage in enumerate(U2):
    Ust.write(i+1, 0, i+1)
    if isinstance(QSVG[i], cp.Variable):
        Ust.write(i+1, 2, QSVG[i].value)
        # print("节点{}的SVG无功功率：{}".format(i+1, QSVG[i].value))
    else:
        Ust.write(i+1, 2, QSVG[i])
    if isinstance(QCB[i], cp.Variable):
        Ust.write(i+1, 3, QCB[i].value)
        # print("节点{}的QCB无功功率：{}".format(i+1, QCB[i].value))
    else:
        Ust.write(i+1, 3, QCB[i])
    if isinstance(PDG[i], cp.Variable):
        print(type(PDG[i].value))
        print(PDG[i].value)
        Ust.write(i+1, 4, PDG[i].value.astype(float))
        # print("发电机节点{}的有功功率：{}，无功功率：{}".format(i+1, PDG[i].value, QDG[i].value))
    else:
        Ust.write(i+1, 4, PDG[i])
    if isinstance(QDG[i], cp.Variable):
        Ust.write(i+1, 5, QDG[i].value)
    else:
        Ust.write(i+1, 5, QDG[i])
    if isinstance(voltage, cp.Variable):
        Ust.write(i+1, 1, voltage.value)
        # print("the voltage of node {} is {}".format(i+1, math.sqrt(voltage.value)))
    else :
        Ust.write(i+1, 1, voltage)
        # print("const votage value of node {} is {}".format(i+1, voltage))
    Ust.write(i+1, 6, PLD[i])
    Ust.write(i+1, 7, QLD[i])
    
    # Ust.write(i+1, 8, P[i].value)
    # Ust.write(i+1, 9, Q[i].value)
lineInfo = wbk.add_worksheet("支路信息")
lineInfo.write(0, 0, "之路起点")
lineInfo.write(0, 1, "之路终点")
lineInfo.write(0, 2, "电流")
lineInfo.write(0, 3, "from功率")
lineInfo.write(0, 4, "to功率")
for index, line in enumerate(lines):
    i = line[1]
    j = line[2]
    lineInfo.write(index+1, 0, i)
    lineInfo.write(index+1, 1, j)
    lineInfo.write(index+1, 2, math.sqrt(Iij2[i-1][j-1].value))
    lineInfo.write(index+1, 3, Pij[i-1][j-1].value)
    lineInfo.write(index+1, 4, Pij[j-1][i-1].value)
    # print("current vlaue of line {} to {} is {}".format(i, j, math.sqrt(Iij2[i-1][j-1].value)))
for i, item in enumerate(N_CB):
    if isinstance(item, cp.Variable):
        print("Capacitor at node {} is in {}".format(i+1, item.value))
pij = wbk.add_worksheet("功率")
Iij = wbk.add_worksheet("电流")
for i in range(n):
    for j in range(n):
        pij.write(i+1, j+1, Pij[i][j].value)
        Iij.write(i+1, j+1, math.sqrt(Iij2[i][j].value))
        # if abs(Pij[i][j].value) > 1e-2:
        #     print("Pij[{}][{}] is {}".format(i+1, j+1, Pij[i][j].value))
wbk.close()