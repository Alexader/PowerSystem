class Line:

    def __init__(self):
        ''' 一条线路模型'''
        # 下面是输入的数据
        # 默认是一条线路，然后每条启用的线路的数据值是一致的
        self.X = 0
        self.R = 0
        self.numberofLines = 1
        self.stateofLines = []
        self.activepowerFrom = 0
        self.activepowerTo = 0
        self.activepower = 0
        self.lossproportion = []
        self.relationalBus = []

        # 下面是应该计算出来的数据
        self.loss = 0
        self.price = 0
        self.lossproportion = 0

    def calcLineLoss(self):
        num = 0
        for state in self.stateofLines:
            if state == 1:
                num += 1
        self.loss = abs(self.activepowerFrom-self.activepowerTo) * num

    def getAveragePrice(self):
        return (self.relationalBus[0].realtimePrice + self.relationalBus[1].realtimePrice) / 2
