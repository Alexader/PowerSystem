#  0     1      2         3        4       5      6       7       8     9  
# 编号 &  U & {\theta} & {P_g} & {Q_g} & {P_L} & {Q_L} & 节点类型& SVG &  CB  
# 0 是平衡节点，1是PQ节点，2是 PV节点
nodes = [
    [1, 1.06,   0,   124, -5, 0,  0,   0, 1, 0],
    [2, 1.02, -4.88, 0,    0, 45, 15,  2, 0, 0],
    [3, 1.02, -5.21, 0,    0, 40, 5,   1, 0, 0],
    [4, 1.05, -2.65, 45,  -3, 20, -20, 1, 1, 1],
    [5, 1.02, -6.01, 0,    0, 60, 10,  1, 0, 0]
]
#   0         1         2        3       4        5         6      7
# 线路编号 & 起始节点 & 结束节点 & {R_1} & {X_1} & {B_1/2} & {变比K}  Pij
lines = [
    [1, 1, 2, 0.08, 0.24, 0.025, 1, 39.93],
    [2, 1, 4, 0.06, 0.06, 0.03, 1, 84.50],
    [3, 2, 3, 0.01, 0.03, 0.01, 1, 18.47],
    [4, 2, 4, 0.06, 0.18, 0.02, 1, -25.05],
    [5, 3, 4, 0.06, 0.18, 0.02, 1, -28.22],
    [6, 3, 5, 0.08, 0.24, 0.025, 1, 6.2],
    [7, 4, 5, 0.04, 0.12, 0.015, 1, 54.96]
]
for node in nodes:
    node[3] = node[3]/100
    node[4] = node[4]/100
    node[5] = node[5]/100
    node[6] = node[6]/100
for line in lines:
    line[7] = line[7]/100
print(nodes)
print(lines)