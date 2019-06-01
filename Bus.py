class Bus:
    def __init__(self):
        ''' 节点模型'''
        # 下面是输入的数据
        self.busType = -1
        self.busNum = 0
        self.U = 1
        self.theta = 0.0
        self.BusActivePower = 0
        self.BusReactivePower = 0
        self.GeneratorActivePower = 0
        self.GeneratorReactivePower = 0
        self.LoadActivePower = 0
        self.LoadReactivePower = 0
        self.SVG = False
        self.CB = False
        self.realtimePrice = 0
        self.lossproportion = []
