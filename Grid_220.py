from Line import Line
from Transformer import Transformer
from Bus import Bus
from Area import Area


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

    def CalcPowerFlowLoss(self):
        for line in self.lines:
            line.calcLineLoss()
