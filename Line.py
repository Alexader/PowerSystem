class Line:

    def __init__(self):
        ''' 一条线路模型'''
        # 下面是输入的数据
        # 默认是一条线路，然后每条启用的线路的数据值是一致的
        self.x = 0
        self.r = 0
        self.numberofLines = 1
        self.stateofLines = []
        self.activepowerfrom = 0
        self.activepowerto = 0
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
        return (self.activepowerfrom-self.activepowerto) * num
    #def updatePrice(self):
