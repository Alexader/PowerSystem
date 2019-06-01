class Transformer:

    def __init__(self):
        ''' 一个变压器模型'''
        # 下面是输入的数据
        self.x = 0
        self.r = 0
        # 默认是一个变压器，然后每条启用的变压器的数据值是一致的
        self.numberofTrans = 1
        self.transState = []
        self.activepowerFrom = 0
        self.activepowerTo = 0
        self.activepower = 0
        self.relationalBus = []
        # 历史占比的数据
        self.lossproportion = []
        # 下面是应该计算出来的数据
        self.loss = 0
        self.cost = 0
        self.lossproportion = 0

    def calcTansformerLoss(self):
        num = 0
        for state in self.transState:
            if state == 1:
                num += 1
        self.loss = abs(self.activepowerFrom - self.activepowerTo) * num

    def getAveragePrice(self):
        return (self.relationalBus[0].realtimePrice + self.relationalBus[1].realtimePrice) / 2