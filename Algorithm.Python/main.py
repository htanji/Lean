"""
SEL(stock selection part)
Based on the 'Momentum Strategy with Market Cap and EV/EBITDA' strategy introduced by Jing Wu, 6 Feb 2018
adapted and recoded by Jack Simonson, Goldie Yalamanchi, Vladimir, Peter Guenther, Leandro Maia and Simone Pantaleoni
https://www.quantconnect.com/forum/discussion/3377/momentum-strategy-with-market-cap-and-ev-ebitda/p1
https://www.quantconnect.com/forum/discussion/9678/quality-companies-in-an-uptrend/p1
https://www.quantconnect.com/forum/discussion/9632/amazing-returns-superior-stock-selection-strategy-superior-in-amp-out-strategy/p1

I/O(in & out part)
The Distilled Bear in & out algo
based on Dan Whitnable's 22 Oct 2020 algo on Quantopian.
Dan's original notes:
"This is based on Peter Guenther great “In & Out” algo.
Included Tentor Testivis recommendation to use volatility adaptive calculation of WAIT_DAYS and RET.
Included Vladimir's ideas to eliminate fixed constants
Help from Thomas Chang"

https://www.quantopian.com/posts/new-strategy-in-and-out
https://www.quantconnect.com/forum/discussion/9597/the-in-amp-out-strategy-continued-from-quantopian/
"""

from AlgorithmImports import *
from QuantConnect.Data.Custom.Tiingo import *
from my_custom_data import CboeVix, CboeVxV

import dateutil
import sendmail
#from YahooFinancePrice import *



local_hosts = {'SF-SA13101': True,
               'egan': True,
               'htanji-PC-LZ750NSB': True,
               'kachidoki': True}
hostname = os.uname()[1]

def isLocal():
    hostname = os.uname()[1]
    return hostname in local_hosts

#if isLocal():
#    from QuantConnect.Data.Custom.YahooFinance import *
from QuantConnect.Data.Custom.YahooFinance import *

class CFD_InOut(QCAlgorithm):

    def addSymbol(self, klass, data, res, leverage):
        equity = self.AddEquity(data, res)
        symbol = (self.AddData(klass, equity.Symbol, res) if isLocal() else data).Symbol
        self.Securities[symbol].SetLeverage(leverage)
        return symbol

    def addLocalSymbol(self,  data, res, leverage):
        equity = self.AddEquity(data, res)
        symbol = equity.Symbol
        self.Securities[symbol].SetLeverage(leverage)
        return symbol

    def addLiveSymbol(self, data, res, leverage):
        symbol = self.AddData(YahooFinancePrice, data, res).Symbol
        self.Securities[symbol].SetLeverage(leverage)
        return symbol

    def addTiingo(self, data, res, leverage = 1):
        if self.LiveMode:
            return self.addLiveSymbol(data, res, leverage)
        return self.addSymbol(TiingoPrice, data, res, leverage)

    def addYahoo(self, data, res, leverage):
        if self.LiveMode:
            return self.addLiveSymbol(data, res, leverage)
        return self.addSymbol(YahooFinancePrice, data, res, leverage)

    def myLog(self, log):
        self.Log(log if not isLocal()
                 else "{}: {}".format(self.Time, log))

    def clear_ObjectStore(self):
        keys = [str(j).split(',')[0][1:]
                for _, j in enumerate(self.ObjectStore.GetEnumerator())]
        for key in keys:
            self.ObjectStore.Delete(key)

    def myInitialize(self):
        self.hostname = os.uname()[1]
        self.myLog('hostname: %s' % self.hostname)

        # Set your Tiingo API Token here
        #Tiingo.SetAuthCode("9a596f5bd73a1470ce69bccb8cd5268db2a72780")
        Tiingo.SetAuthCode("6c44375f029af567186df2b7434dcf324688ec5b")


    def Initialize(self):

        self.myInitialize()
        res = Resolution.Daily if not self.LiveMode else Resolution.Minute

        start_date = self.GetParameter("start-date")
        end_date = self.GetParameter("end-date")

        self.myLog('param start date {}'.format(start_date))
        self.myLog('param end date {}'.format(end_date))

        if isLocal() and start_date == '':
            start_date = '2021/12/08'
        #if isLocal() and end_date == '':
        #    end_date = str(datetime.today())

        self.myLog('start date {}'.format(start_date))
        self.myLog('end date {}'.format(end_date))

        if False:
            self.myLog(os.environ)

        if start_date:
            self.SetStartDate(dateutil.parser.parse(start_date))

        if end_date:
            self.SetEndDate(dateutil.parser.parse(end_date))

        #in_leverage = float(self.GetParameter("IN_LEVERAGE"))
        #out_leverage = float(self.GetParameter("OUT_LEVERAGE"))
        #bear_gold_hold = float(self.GetParameter("BEAR_GOLD_HOLD"))
        #bear_vix_hold = float(self.GetParameter("BEAR_VIX_HOLD"))
        #self.cob_ratio = int(self.GetParameter("COB_RATIO"))
        #self.dzma_in_ratio = float(self.GetParameter("DZMA_IN_RATIO"))
        #self.dzma_out_ratio = float(self.GetParameter("DZMA_OUT_RATIO"))

        in_leverage = 1.0
        out_leverage = 1.0
        bear_gold_hold = 3.0
        bear_vix_hold = 0.0
        self.cob_ratio = 25
        self.dzma_in_ratio = 0.0
        self.dzma_out_ratio = 0.0

        # inception date
        # QQQ 1999/3/10
        # SLV 2006/4/28
        # TLT 2002/7/22
        # IEF 2002/7/22
        # GOLD 2014/5/16
        # XLU 1998/12/16
        # XLI 1998/12/16
        # DBB 2007/1/5
        # UUP 2007/2/20

        # self.SetStartDate(2021, 11, 1)  #Set Start Date
        # self.SetStartDate(1999, 1, 1)  #Set Start Date
        # self.SetStartDate(2008, 1, 1)  #Set Start Date
        # self.SetStartDate(2012, 1, 1)  #Set Start Date
        # self.SetStartDate(2021, 1, 1)  #Set Start Date
        # self.SetEndDate(2021, 1, 1)  #Set Start Date
        # self.SetStartDate(2021, 9, 1)  # Set Start Date
        # self.SetStartDate(2021, 12, 6)  # Set Start Date
        # self.SetStartDate(2021, 12, 7)  # Set Start Date
        # self.SetStartDate(2021, 12, 8)  # Set Start Date
        # self.SetStartDate(2021, 12, 9)  # Set Start Date
        # self.SetStartDate(2021, 12, 10)  # Set Start Date
        # self.SetEndDate(2021, 12, 1)  #Set Start Date
        self.cap = 100000
        self.SetCash(self.cap)
        # self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        # self.SetBrokerageModel(BrokerageName.OandaBrokerage, AccountType.Margin)

        # Holdings
        # 'Out' holdings and weights
        self.BND1 = self.addTiingo('TLT', res, 5) # 20+yrs
        self.BND2 = self.addTiingo('IEF', res, 5) # 7yrs
        self.BND3 = self.addTiingo('SHY', res, 5) # 7yrs
        #self.VIX = self.addYahoo("^VIX", res, 10)

        if True and isLocal():
            # YahooFinancePriceを使用する
            self.STKS = self.addYahoo("^NDX", res, 10)
        elif not isLocal():
            self.STKS = self.AddCfd(
                "NAS100USD", res, Market.Oanda, True, 10).Symbol
        elif True:
            self.STKS = self.addLocalSymbol("NAS5", res, 10)
        else:
            self.STKS = self.addTiingo("QQQ", res, 10)

        self.HLD_IN = {self.STKS: in_leverage}

        ##### In & Out parameters #####
        # Feed-in constants
        self.INI_WAIT_DAYS = 15  # out for 3 trading weeks
        self.wait_days = self.INI_WAIT_DAYS

        # Market and list of signals based on ETFs
        self.MRKT = self.addTiingo('SPY', res, 10)  # market
        self.GOLD = self.addTiingo('GLD', res, 20)  # gold
        self.SLVA = self.addTiingo('SLV', res, 20)  # vs silver
        self.UTIL = self.addTiingo('XLU', res)  # utilities
        self.INDU = self.addTiingo('XLI', res)  # vs industrials
        self.METL = self.addTiingo('DBB', res)  # input prices (metals)
        self.USDX = self.addTiingo('UUP', res)  # safe haven (USD)
        self.FNCE = self.addTiingo('XLF', res)  # financial

        # SVXY inception date 10/3/2011
        # UVXY inception date 10/3/2011
        # VXX inception date 1/29/2009

        # add the #2 ETFs (short and long VIX futures)
        # swap xiv with svxy, since xiv is wiped out.
        self.XIV = self.addTiingo("SVXY", res, 5) # switched to svxy
        #self.VXX = self.addTiingo("ZIV", res) # switched to ziv
        self.VXX = self.addTiingo("UVXY", res, 5)
        self.SPY = self.MRKT
        self.SHY = self.BND3
        self.GLD = self.GOLD
        self.DBO = self.addTiingo("DBO", res, 20)
        self.VIX = self.addYahoo("^VIX", res, 10)
        self.VXV = self.addYahoo("^VIX3M", res, 10)

        #self.HLD_BEAR = { self.SHY: bear_leverage - bear_vix_hold, self.VXX: bear_vix_hold }
        self.HLD_BEAR = { self.GLD: bear_gold_hold, self.VIX: bear_vix_hold }

        #self.HLD_BEAR = { self.GLD: 1.5, self.DBO: 1.5, self.VIX: 0.5 }
        #self.HLD_BEAR = { self.GLD: 1.4, self.VXX: 0.6 }
        #self.HLD_BEAR = { self.SHY: 0.4, self.VXX: 0.6 }

        #self.HLD_OUT = { self.GLD: 2.9, self.VIX: 0.1 }
        self.HLD_OUT = { self.GLD: out_leverage }
        #self.HLD_OUT = {self.BND1: 3.5}

        self.VIX_MA_SLOW = int(self.GetParameter("VIX_MA_SLOW"))
        self.VIX_MA_FAST = int(self.GetParameter("VIX_MA_FAST"))

        #if not self.LiveMode:
        self.SetBenchmark("SPY")
        #self.SetWarmUp(252 * 2)
        
        # Define symbol and "type" of custom data: used for signal ratio
        #self.VIX = self.AddData(CboeVix, "VIX").Symbol
        #self.VXV = self.AddData(CboeVxV, "VXV").Symbol
        
 
        self.symbols = [self.MRKT, self.GOLD, self.SLVA, self.UTIL, self.INDU, self.METL, self.USDX, self.FNCE, self.BND1, self.BND2, self.VIX, self.VXV]

        # Specific variables
        self.DISTILLED_BEAR = False
        self.VOLA_LOOKBACK = int(self.GetParameter("VOLA_LOOKBACK"))
        self.WAITD_CONSTANT = int(self.GetParameter("WAITD_CONSTANT"))
        self.DCOUNT = 0  # count of total days since start
        # dcount when self.be_in=0, initial setting ensures trading right away
        self.OUTDAY = (-self.INI_WAIT_DAYS+1)
        self.MARKET_STATUS = None
        self.BEAR_UPTREND = False
        self.BEAR_STOP_AND_REVERSE = False

        self.Debug('VOLA_LOOKBACK={} WAITD_CONSTANT={}'.format(self.VOLA_LOOKBACK, self.WAITD_CONSTANT))

        if not self.LiveMode:
            self.myLog('clear store')
            self.clear_ObjectStore()

        if self.ObjectStore.ContainsKey('data'):
            # our object store has our historical data saved, read the data
            # and push it through the indicators to warm everything up
            data = self.ObjectStore.Read('data')
            # self.myLog(data)
            data = json.loads(data)
            self.DCOUNT = data['DCOUNT']
            self.OUTDAY = data['OUTDAY']
            self.myLog("Restore state: DCOUNT={} OUTDAY={}".format(
                self.DCOUNT, self.OUTDAY))

        # set a warm-up period to initialize the indicator
        #self.SetWarmUp(timedelta(days=self.VOLA_LOOKBACK), Resolution.Daily)
        #self.SetWarmUp(365, Resolution.Daily)
        #self.SetWarmUp(self.VOLA_LOOKBACK * 2)

        # Benchmark = record SPY
        self.spy = []

	# History生成
        # BarCount分読み込んでくれないため、多めに読み込む
        history = self.History(self.symbols, 252 * 3, Resolution.Daily)
        # 終値のみ保存する
        self.history_all = pd.DataFrame()
        for symbol in self.symbols:
            self.history_all[symbol] = history.xs(symbol, level='symbol')['close']

        # Setup daily consolidation
        for symbol in self.symbols:
            self.consolidator = TradeBarConsolidator(timedelta(days=1))
            self.consolidator.DataConsolidated += self.consolidation_handler
            self.SubscriptionManager.AddConsolidator(symbol, self.consolidator)

        #delay = 30 if not isLocal() or self.LiveMode else 0
        delay = 30

        self.Schedule.On(
            self.DateRules.EveryDay(),
            self.TimeRules.AfterMarketOpen('SPY', delay),  # reduced time
            self.rebalance_when_out_of_the_market)

        self.Schedule.On(
            self.DateRules.EveryDay(),
            self.TimeRules.BeforeMarketClose('SPY', 0) if not self.LiveMode
            else self.TimeRules.Every(timedelta(minutes=1)),
            self.record_vars)

        # Set the security initializer with the characteristics defined in CustomSecurityInitializer
        self.SetSecurityInitializer(self.CustomSecurityInitializer)

        #self.SetWarmUp(252 * 2)

        # initialize the indicator with the daily history close price
        #history = self.History(["SPY"], 10, Resolution.Daily)
        #for time, row in history.loc["SPY"].iterrows():
        #    self.rsi.Update(time, row["close"])

        
        self.window_len = 252
        self.situation = False
        self.cob = None
        self.dzma = None

        self.dzma_average = EmaData(self) 

        # initialize the indicator with the daily history close price
        for i in range(-self.window_len + 1, 0): 
        #for i in range(-10 + 1, 0): 
            self.myLog(i)
            self.Balance(self.history_all[:i][-self.window_len:])
        self.Balance(self.history_all[-self.window_len:])

        alert = 'Starting algorithm'
        self.alert(alert, alert)


    def alert(self, subject, body):
        self.myLog("{} {}".format(subject, body))
        to = "hideki.tanji+qc@gmail.com"
        self.Notify.Sms("+819088927994", body)
        self.Notify.Email(to, subject, body)
        if False and self.LiveMode:
            sendmail.sendmail(subject, body, 'hideki.tanji@gmail.com', to)

    def consolidation_handler(self, sender, consolidated):
        self.myLog("update {} {}".format(consolidated.EndTime, consolidated))
        #self.myLog(self.history)
        #self.myLog("update {} {} {}".format(self.Time, consolidated.Symbol, consolidated.EndTime))
        #    self.myLog('nan: {}'.format(consolidated.Symbol))
        self.history_all.loc[consolidated.EndTime,
                             consolidated.Symbol] = consolidated.Close


    def derive_vola_waitdays(self):
        volatility = np.log1p(self.history[self.MRKT].pct_change()
                     ).std() * np.sqrt(self.VOLA_LOOKBACK)
        wait_days = int(volatility * self.WAITD_CONSTANT)
        returns_lookback = int((1.0 - volatility) * self.WAITD_CONSTANT)
        return wait_days, returns_lookback

    
    def liquidate(self, stock):
        for symbol in stock:
            if self.Portfolio[symbol].Invested:
                self.myLog("SELL {}".format(symbol))
                self.Liquidate(symbol)

    def set_holdings(self, stock):
        for symbol, count in stock.items():
            if not self.Portfolio[symbol].Invested:
                self.myLog("BUY {} {}".format(symbol, count))
                self.SetHoldings(symbol, count)

    def update_from_history(self):
        history_day = self.History(self.symbols, 1, Resolution.Daily)
        if not history_day.empty:
            for symbol in self.symbols:
                close = history_day.xs(symbol, level='symbol')['close']
                self.history_all[symbol].append(close)

    def rebalance_when_out_of_the_market(self):
        #self.myLog('rebalance_when_out_of_the_market')
        found = False
        for t in self.history_all.index:
            if t.date() == self.Time.date():
                found = True
        if found:
            self.myLog('use consolidator')
        else:
            # 起動初日はコンソリデータが動かないためヒストリを使用
            self.myLog('use history')
            self.history = self.update_from_history()
        self.history = self.history_all[-self.VOLA_LOOKBACK:]
        self.myLog(self.history)
            
        self.wait_days, returns_lookback = self.derive_vola_waitdays()
        # Check for Bears
        returns = self.history.pct_change(returns_lookback).iloc[-1]

        silver_returns = returns[self.SLVA]
        gold_returns = returns[self.GOLD]
        industrials_returns = returns[self.INDU]
        utilities_returns = returns[self.UTIL]
        metals_returns = returns[self.METL]
        dollar_returns = returns[self.USDX]
        financial_returns = returns[self.FNCE]
        bond_20yrs_returns = returns[self.BND1]
        bond_7yrs_returns = returns[self.BND2]

        False and self.myLog('returns SLV={:.2f} GLD={:.2f} IND={:.2f} UTL={:.2f} MTL={:.2f} DLR={:.2f} FIN={:.2f} 20Y={:.2f} 7Y={:.2f} G_S={} U_I={} M_D={} WD={} LB={}'.format(
            silver_returns,
            gold_returns,
            industrials_returns,
            utilities_returns,
            metals_returns,
            dollar_returns,
            financial_returns,
            bond_20yrs_returns,
            bOond_7yrs_returns,
            gold_returns > silver_returns,
            utilities_returns > industrials_returns,
            metals_returns < dollar_returns,
            self.wait_days,
            returns_lookback))

        self.DISTILLED_BEAR = (((gold_returns > silver_returns) and \
                            (utilities_returns > industrials_returns)) and \
                            (metals_returns < dollar_returns))

        self.FINANCIAL_SHOCK = (bond_7yrs_returns > financial_returns) and \
            (bond_20yrs_returns > financial_returns)

        # Determine whether 'in' or 'out' or 'weak' of the market
        market_status = None
        # 初回は必ず購入
        be_in = (self.MARKET_STATUS == None)

        if self.DISTILLED_BEAR:
            be_in = False
            self.OUTDAY = self.DCOUNT

        if self.DCOUNT >= self.OUTDAY + self.wait_days:
            be_in = True

        True and self.myLog('IN = {} BEAR = {} PREV = {}'.format(be_in, self.DISTILLED_BEAR, self.MARKET_STATUS))

        if self.DISTILLED_BEAR or not be_in:
            market_status = 'OUT'
        else:
            market_status = 'IN'

        # VIX strat
        situation = self.situation
        dzma = self.dzma
        bear_uptrend = self.dzma_average.is_uptrend

        True and self.myLog('situation = {} dzma = {} bear_uptrend = {}'.format(situation, dzma, bear_uptrend))

        if self.MARKET_STATUS == 'BEAR' and \
           self.BEAR_UPTREND and not bear_uptrend:
            # ベアトレンド終了
            self.BEAR_STOP_AND_REVERSE = True

        elif self.BEAR_STOP_AND_REVERSE and \
             situation and dzma >= self.dzma_in_ratio:
            # ドテン買い期間
            pass

        elif self.BEAR_STOP_AND_REVERSE:
            # ドテン買い期間終了
            self.BEAR_STOP_AND_REVERSE = False
                        
        elif self.MARKET_STATUS != 'OUT' and \
             situation and dzma >= self.dzma_in_ratio:
            market_status = 'BEAR'

        if market_status == self.MARKET_STATUS:
            # no change
            pass
        elif market_status == 'IN':
            self.alert("Live Trade Signal Generated [IN]", "Market in now!!")
            self.liquidate(self.HLD_OUT)
            self.liquidate(self.HLD_BEAR)
            self.set_holdings(self.HLD_IN)

        elif market_status == 'OUT':
            self.alert("Live Trade Signal Generated [OUT]", "Market out now!!")
            self.liquidate(self.HLD_IN)
            self.liquidate(self.HLD_BEAR)
            self.set_holdings(self.HLD_OUT)

        elif market_status == 'BEAR':
            self.alert("Live Trade Signal Generated [BEAR]", "Market bear now!!")
            self.liquidate(self.HLD_IN)
            self.liquidate(self.HLD_OUT)
            self.set_holdings(self.HLD_BEAR)
        else:
            self.Error('code error')

        if False and not 'BACKTESTING' in hostname:
            #self.myLog(self.history)
            wait_left = (self.OUTDAY + self.wait_days) - self.DCOUNT  if not be_in else 0
            self.myLog("LEFT={} STAT={} DISTILLED_BEAR={} FINANCIAL_SHOCK={} DCOUNT={} OUTDAY={} wait_days={} equity={:.0f} margin={:.0f} margin_used={:.0f} unrealized={:.0f} holding={:.0f}".format(
                wait_left, self.MARKET_STATUS, self.DISTILLED_BEAR, self.FINANCIAL_SHOCK, self.DCOUNT, self.OUTDAY, self.wait_days, self.Portfolio.TotalPortfolioValue, self.Portfolio.MarginRemaining, self.Portfolio.TotalMarginUsed, self.Portfolio.TotalUnrealizedProfit, self.Portfolio.TotalHoldingsValue))

        self.MARKET_STATUS = market_status
        self.BEAR_UPTREND = bear_uptrend
        self.DCOUNT += 1

    def record_vars(self):
        self.spy.append(self.history_all[self.MRKT].dropna().iloc[-1])
        spy_perf = self.spy[-1] / self.spy[0] * self.cap
        self.Plot('Strategy Equity', 'SPY', spy_perf)

        account_leverage = self.Portfolio.TotalHoldingsValue / \
            self.Portfolio.TotalPortfolioValue
        self.Plot('Holdings', 'leverage', round(account_leverage, 2))
        self.Plot('Margin', 'remain', self.Portfolio.MarginRemaining)
        #self.myLog('Margin remain {} value {}'.format(self.Portfolio.MarginRemaining, self.Portfolio.TotalPortfolioValue))

        #if self.Portfolio.MarginRemaining < 0:
        #    self.myLog('Margin call {}'.format(self.Portfolio.MarginRemaining))

        data = {'DCOUNT': self.DCOUNT, 'OUTDAY': self.OUTDAY}
        self.ObjectStore.Save('data', json.dumps(data))



    def OnOrderEvent(self, orderEvent):
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        if orderEvent.Status == OrderStatus.Filled: 
            self.Log("Filled: {0}: {1}: {2}".format(self.Time, order.Type, orderEvent))
            pass



    def OnMarginCall(self, requests):

        # Margin call event handler. This method is called right before the margin call orders are placed in the market.
        # <param name="requests">The orders to be executed to bring this algorithm within margin limits</param>
        # this code gets called BEFORE the orders are placed, so we can try to liquidate some of our positions
        # before we get the margin call orders executed. We could also modify these orders by changing their quantities
        self.myLog('OnMarginCall Margin remain {} value {}'.format(self.Portfolio.MarginRemaining, self.Portfolio.TotalPortfolioValue))

        for order in requests:

            # liquidate an extra 10% each time we get a margin call to give us more padding
            newQuantity = int(order.Quantity * 1.1)
            #self.Log('request {} {} {} {}'.format(order.Symbol, self.Portfolio[order.Symbol].Quantity, order.Quantity, newQuantity))
            requests.remove(order)
            requests.append(SubmitOrderRequest(order.OrderType, order.SecurityType, order.Symbol, newQuantity, order.StopPrice, order.LimitPrice, self.Time, "OnMarginCall"))
            self.Error("{} - OnMarginCall(): Liquidating {} shares of {}.".format(self.Time, newQuantity, order.Symbol))

        return requests

    def OnMarginCallWarning(self):

        # Margin call warning event handler.
        # This method is called when Portfolio.MarginRemaining is under 5% of your Portfolio.TotalPortfolioValue
        # a chance to prevent a margin call from occurring
        self.myLog('OnMarginCallWarning Margin remain {} value {}'.format(self.Portfolio.MarginRemaining, self.Portfolio.TotalPortfolioValue))

        for sec in self.Securities.Values:
            #spyHoldings = self.Securities["SPY"].Holdings.Quantity
            if not sec.Holdings.Invested:
                continue
            holdings = sec.Holdings.Quantity
            shares = int(-holdings * 0.005)
            self.Error("{} - OnMarginCallWarning(): Liquidating {} shares of {} to avoid margin call.".format(self.Time, shares, sec))
            self.MarketOrder(sec, shares)

    def CustomSecurityInitializer(self, security):
        '''Initialize the security with raw prices and zero fees 
        Args:
            security: Security which characteristics we want to change'''
        #security.SetDataNormalizationMode(DataNormalizationMode.Raw)
        security.SetFeeModel(ConstantFeeModel(0))

    def OnEndOfAlgorithm(self):
        self.myLog('OnEndOfAlgorithm')
        self.Log("TotalPortfolioValue: {}".format(self.Portfolio.TotalPortfolioValue))

    # TODO: verify data correctness.
    # TODO: is there a better way to collect data?    
    def OnData(self, data):
        for value in data.values():
            self.myLog('OnData {}'.format(value))

    def Balance(self, history):
        self.myLog('Balance')

        # TODO: compute needs to be moved to ??? alpha compute method.
        # then alpha can be used to aid in construct portfolio.

        time = history.iloc[-1].name
        
        vix_price = history[self.VIX]
        vxv_price = history[self.VXV]
        
        #self.myLog(vix_price)
        #self.myLog(vxv_price)
        
        # OnDataで取得するデータは前日のデータのため、
        # 現状では先読みバイアスは発生しない。
        # 01/01のデータは12/31のデータであることを確認。
        
        cob = vix_price / vxv_price
        
        # compute momentum of cob.
        # get z score of cob. if z score increases
        # it is likely that backwardation would happen
        mean = cob.rolling(126).mean()
        sd = cob.rolling(126).std()
        z = cob - mean / sd
        dz  = z.pct_change()
        dzma = dz.rolling(5).mean()
        
        cobma = cob.rolling(10).median() # "Strategy 3, Vratio10 by Tony Cooper"
        self.cob = cobma.iloc[-1]
        self.dzma = dzma.iloc[-1]
        
        True and self.myLog("VIX: {},{},{},{},{}".format(
            time,
            vix_price.iloc[-1],
            vxv_price.iloc[-1],
            self.cob, self.dzma))

        self.situation = (self.cob > np.nanpercentile(cob, [self.cob_ratio])[0])

        self.dzma_average.update(time, self.dzma)

        # cob = vix/vxv
        # cob < 1 , vix < vxv: contago
        # cob > 1 , vix > vxv: backwardation (1 mnth more expensive than 3 mnth future)
        # https://en.wikipedia.org/wiki/Contango
        # https://en.wikipedia.org/wiki/Normal_backwardation
        # 
        # np.nanpercentile(df['VIX/VXV'],[30,40,50,60,70,80,90])
        # >>> array([0.86649373, 0.88454818, 0.9025271 , 0.92344436, 0.94629521, 0.97491226, 1.01362785])
        
        #
        #     ___o .--.
        #   /___| |OO|
        #   /'   |_|  |_
        #       (_    _)
        #       | |   \
        #       | |oo_/sjw
        #
        # Don't say Tony Cooper didn't warn you about the Grim Reaper.

        # !prioritize fear
        # long volatility if trending towards backwardation at any time
        #if cob > 0.88 and dzma > 0:


class EmaData(object):
    def __init__(self, qa):
        self.qa = qa
        self.tolerance = 1.01
        self.fast = ExponentialMovingAverage(qa.VIX_MA_FAST)
        self.slow = ExponentialMovingAverage(qa.VIX_MA_SLOW)
        self.is_uptrend = False
        self.scale = 0

    def update(self, time, value):
        #EmaData.qa.myLog('update time {} value {}'.format(time, value))
        if self.fast.Update(time, value) and self.slow.Update(time, value):
            fast = self.fast.Current.Value
            slow = self.slow.Current.Value
            self.is_uptrend = fast > slow * self.tolerance
            #EmaData.qa.myLog('uptrend {} fast_e {} slow_e {}'.format(self.is_uptrend, fast, slow))

        if self.is_uptrend:
            self.scale = (fast - slow) / ((fast + slow) / 2.0)
