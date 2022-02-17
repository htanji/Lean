from AlgorithmImports import *
from QuantConnect.Data.Custom.YahooFinance import *

class Test(QCAlgorithm):

    def Initialize(self):

        self.SetStartDate(2021, 1, 9)
        #self.SetEndDate(2021, 2, 1)

        self.ticker = "GC=F"
        #self.AddData(YahooFinancePrice, self.ticker, Resolution.Minute)
        self.AddData(YahooFinancePrice, self.ticker, Resolution.Second)
        #self.AddData(Bitcoin, 'BTC', Resolution.Second, TimeZones.Utc)
        history = self.History(self.ticker, 2, Resolution.Daily)
        self.Log(history)

        #qqq = self.AddEquity('QQQ')
        #qqq = self.AddEquity('^NDX')
        #qqq2 = self.AddData(YahooFinancePrice, qqq.Symbol)
        #history = self.History(qqq2.Symbol, 2, Resolution.Daily)
        #self.Log(self.Time)
        #self.Log(history)
        #self.qqq = qqq2.Symbol

    def OnData(self, slice):
        self.Log('OnData {}'.format(slice[self.ticker].Price))
        if not self.Portfolio.Invested:
            self.SetHoldings(self.ticker, 1)
