import backtrader as bt

class CustomMA(bt.Indicator):
    lines = ('custom_ma',)
    params = dict(period=15)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        self.lines.custom_ma[0] = sum(self.data.close.get(size=self.params.period)) / self.params.period

class CustomRSI(bt.Indicator):
    lines = ('custom_rsi',)
    params = dict(period=14)

    def __init__(self):
        self.addminperiod(self.params.period)
        self.gains = [0] * self.params.period
        self.losses = [0] * self.params.period

    def next(self):
        gain = 0
        loss = 0
        for i in range(1, self.params.period + 1):
            change = self.data.close[-i + 1] - self.data.close[-i]
            if change > 0:
                gain += change
            else:
                loss -= change

        avg_gain = gain / self.params.period
        avg_loss = loss / self.params.period
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        self.lines.custom_rsi[0] = 100 - (100 / (1 + rs))
