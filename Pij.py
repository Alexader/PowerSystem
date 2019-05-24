import json
import numpy as np
import cvxpy as cp

# 读入电网结构的信息
with open("powerFlow.json", "r") as read_file:
	data = json.load(read_file)
nodeInfo = data["node"]
lines = data["lines"]

m = len(lines)
n = len(nodeInfo)

Pij = []
Qij = []
U = np.zeros(n, dtype=complex)
realU = np.zeros(n)
theta = np.zeros(n)
R = np.zeros((n, n), dtype=np.complex128)
X = np.zeros((n, n), dtype=np.complex128)
Y = np.zeros((n, n), dtype=np.complex128)
S = np.zeros((n, n), dtype=np.complex128)

for i, node in enumerate(nodeInfo):
	# item 为list类型
	#  0     1      2         3        4       5      6       7       8     9   10
	# 编号 &  U & {\theta} & {P_g} & {Q_g} & {P_L} & {Q_L} & 节点类型& SVG &  CB  
	# 0 是平衡节点，1是PQ节点，2是 PV节点
	U[i] = node[1]*np.sin(node[2]*np.pi/180) + 1j*node[1]*np.cos(node[2]*np.pi/180)

nodeNum2LineNum = {}
for line in lines:
	# lines 为 矩阵形式的 list
	# line :
	#   0         1         2        3       4        5         6
	# 线路编号 & 起始节点 & 结束节点 & {R_1} & {X_1} & {B_1/2} & {变比K}
	i = line[1]-1
	j = line[2]-1
	# Y[i][j] += -1.0/((line[3]+line[4]*1j)*line[6])
	# Y[j][i] = Y[i][j]
	# Y[i][i] += 1.0/((line[3]+line[4]*1j)*(line[6]**2)) + line[5]
	# Y[j][j] += 1.0/(line[3]+line[4]*1j) + line[5]
	Y[i][j] = Y[j][i] = 1.0/(line[3]-line[4]*1j)
	nodeNum2LineNum[(i, j)] = nodeNum2LineNum[(j, i)] = line[0]-1
	R[i][j] = R[j][i] = line[3]
	X[i][j] = X[j][i] = line[4]
cnt =0
for i in range(n):
	for j in range(n):
		yi0 = 0
		if (i+1, j+1) in nodeNum2LineNum:
			yi0 = lines[nodeNum2LineNum[(i+1, j+1)]][5]*1j
			print(yi0)
		S[i][j] = U[i]**2*yi0 + U[i]*(np.conj(U[i]) - np.conj(U[j]))*Y[i][j]

Pij = np.real(S)
cnt =0
for item in Pij:
	for i in item:
		if i != 0:
			cnt =  cnt+1
			print(i)
print(cnt)
with open("data.json", 'r+') as append_file:
	data = json.load(append_file)
	with open("Pij.json", 'r') as read_file:
		Pijdict = json.load(read_file)
		Pij = Pijdict["Pij"]
	lines = data["lines"]
	for line in lines:
		i = line[1] - 1
		j = line[2] - 1
		line.append(Pij[i][j])
		print(Pij[i][j])

# with open('data.json', 'w') as f:
# 	json.dump(data, f, indent=4)
# X = []
# Y = [1,0,1,1,0]
# for i in Y:
# 	if i==0:
# 		X.append(1.0)
# 	else :
# 		X.append(cp.Variable())

# for item in X:
# 	if(isinstance(item, cp.Variable)):
# 		print("yes")
# 	else:
# 		print("No")