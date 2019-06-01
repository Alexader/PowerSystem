from Grid_220 import Grid220
from Line import Line
from Transformer import Transformer
from Area import Area
import json

# 构建一个的矩阵，并存入文件中
nodeInfo = []
lineInfo = []
grid = Grid220()
for line in grid.lines:
    #   0         1         2        3       4        5         6      7    8
    # 线路编号 & 起始节点 & 结束节点 & {R_1} & {X_1} & {B_1/2} & {变比K}  Pij  Ploss
    tmpLine = [0 for i in range(10)]
    tmpLine[0] = line.lineNum
    tmpLine[1] = line.startNode
    tmpLine[2] = line.endNode
    tmpLine[3] = line.R
    tmpLine[4] = line.X
    tmpLine[5] = line.B
    tmpLine[6] = line.K
    tmpLine[7] = line.activePowerFrom
    tmpLine[8] = line.loss
    tmpLine[9] = line.maxCurrent
    lineInfo.append(tmpLine)

for bus in grid.buses:
    #  0     1      2         3        4       5      6       7       8     9     10     11
    # 编号 &  U & {\theta} & {P_g} & {Q_g} & {P_L} & {Q_L} & 节点类型& SVG &  CB  maxCB minCB
    # 0 是平衡节点，1是PQ节点，2是 PV节点
    tmpNode = [0 for i in range(10)]
    tmpNode[0] = bus.busNum
    tmpNode[1] = bus.U**2
    tmpNode[2] = bus.theta
    tmpNode[3] = bus.GeneratorActivePower
    tmpNode[4] = bus.GeneratorReactivePower
    tmpNode[5] = bus.LoadActivePower
    tmpNode[6] = bus.LoadReactivePower
    tmpNode[7] = bus.busType
    tmpNode[8] = bus.SVG
    tmpNode[9] = bus.CB
    tmpNode[10] = bus.maxNCB
    tmpNode[11] = bus.minNCB
    nodeInfo.append(tmpNode)

with open("data.json", "r+") as write_file:
    json.dump({"nodeInfo": nodeInfo, "lineInfo": lineInfo}, write_file, indent=4)
