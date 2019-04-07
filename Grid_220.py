from Line import Line
from Transformer import Transformer
from Bus import Bus
from Area import Area
import cvxpy as cp
import numpy as np


class Grid220:

    def __init__(self, lines, transformers, buses, areas):
        self.lines = lines
        self.transformers = transformers
        self.buses = buses
        self.areas = areas
        self.buspriceAverage = 0
        return 'this is a grid 220kv'

    def calcAveragePrice(self):
        count = 0
        sum = 0
        for bus in self.buses:
            count += 1
            sum += bus.realtimePrice
        self.buspriceAverage = sum / count

    def calcLinePowerFlowLoss(self):
        for line in self.lines:
            line.calcLineLoss()

    def calcTransformerPowerFlowLoss(self):
        for transformer in self.transformers:
            transformer.calcTansformerLoss()

    def calcLinePriceLoss(self):
        '''计算线路损耗的经济损失'''
        for line in self.lines:
            line.cost = line.cost * line.getAveragePrice()

    def calcTransformerPriceLoss(self):
        '''计算变压器损耗的经济损失'''
        for transformer in self.transformers:
            transformer.cost = transformer.loss * transformer.getAveragePrice()

    def calcLinelossProportion(self):
        for line in self.lines:
            line.lossproportion = line.loss / line.activepower

    def calcTransformerLossProportion(self):
        for transformer in self.transformers:
            transformer.lossproportion = transformer.loss / transformer.activepower

    def getArea(self):
        '''如何划分网络的区域'''

    def lossJudge(self):
        '''如何判断那个区域是最需要进行网损优化的区域'''

    def optimize(self):
        m = 20
        n = 30
        