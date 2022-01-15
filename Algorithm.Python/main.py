from AlgorithmImports import *
from QuantConnect.Data.Custom.Tiingo import *
from QuantConnect.Data.Custom.YahooFinance import *
import dateutil


class Test(QCAlgorithm):

    def isLocal(self):
        return True

    def addTiingo(self, data, res):
        return (self.AddData(TiingoPrice, data.Symbol, res) if self.isLocal() else data).Symbol
        # return data.Symbol

    def addYahoo(self, data, res):
        return (self.AddData(YahooFinancePrice, data.Symbol, res) if self.isLocal() else data).Symbol

    def myLog(self, log):
        self.Log(log if not self.isLocal()
                 else "{}: {}".format(self.Time, log))

    def Initialize(self):

        start_date = '2021/12/08'
        end_date = str(datetime.today())

        self.SetStartDate(dateutil.parser.parse(start_date))
        self.SetEndDate(dateutil.parser.parse(end_date))

        self.cap = 100000
        self.SetCash(self.cap)

        Tiingo.SetAuthCode("6c44375f029af567186df2b7434dcf324688ec5b")

        res = Resolution.Minute if not self.isLocal() else Resolution.Daily

        self.BND1 = self.addTiingo(self.AddEquity('TLT', res), res) # 20+yrs
        self.BND2 = self.addTiingo(self.AddEquity('IEF', res), res) # 7yrs
        self.VIX  = self.addTiingo(self.AddEquity('VXXB', res), res) # VIX

        self.MRKT = self.addTiingo(self.AddEquity('SPY', res), res)  # market
        self.GOLD = self.addTiingo(self.AddEquity('GLD', res), res)  # gold
        self.SLVA = self.addTiingo(self.AddEquity('SLV', res), res)  # vs silver
        self.UTIL = self.addTiingo(self.AddEquity('XLU', res), res)  # utilities
        self.INDU = self.addTiingo(self.AddEquity('XLI', res), res)  # vs industrials
        self.METL = self.addTiingo(self.AddEquity('DBB', res), res)  # input prices (metals)
        self.USDX = self.addTiingo(self.AddEquity('UUP', res), res)  # safe haven (USD)
        self.FNCE = self.addTiingo(self.AddEquity('XLF', res), res)  # financial

        self.symbols = [self.MRKT, self.GOLD, self.SLVA, self.UTIL, self.INDU, self.METL, self.USDX, self.FNCE, self.BND1, self.BND2]

        if True:
            for symbol in self.symbols:
                self.consolidator = TradeBarConsolidator(timedelta(days=1))
                self.consolidator.DataConsolidated += self.consolidation_handler
                self.SubscriptionManager.AddConsolidator(symbol, self.consolidator)

        self.History(self.symbols, 10, Resolution.Daily)

    def consolidation_handler(self, sender, consolidated):
        self.myLog("update {} {}".format(self.Time, consolidated))

