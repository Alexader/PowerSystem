class Transformer:

    def __init__(self):
        ''' 一个变压器模型'''
        # 下面是输入的数据
        self.x = 0
        self.r = 0
        # 默认是一条线路，然后每条启用的变压器的数据值是一致的
        self.numberofTrans = 0
        self.TransState = []
        self.activepowerFrom = 0
        self.activepowerTo = 0
        self.activepower = 0
        self.relationalBus = []
        # 历史占比的数据
        self.lossproportion = []
        # 下面是应该计算出来的数据
        self.loss = 0
        self.price = 0
        self.lossproportion = 0

        def calcTansformerLoss(self):
            return (self.activepowerFrom - self.activepowerTo)*self.numofTrans

