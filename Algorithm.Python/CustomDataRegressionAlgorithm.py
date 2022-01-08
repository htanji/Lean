# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from AlgorithmImports import *
from QuantConnect.Data.Custom.Tiingo import *
#import json
#import datetime

### <summary>
### Regression test to demonstrate importing and trading on custom data.
### </summary>
### <meta name="tag" content="using data" />
### <meta name="tag" content="importing data" />
### <meta name="tag" content="custom data" />
### <meta name="tag" content="crypto" />
### <meta name="tag" content="regression test" />


class CustomDataRegressionAlgorithm(QCAlgorithm):
    def Initialize(self):

        self.SetStartDate(2011,9,13)   # Set Start Date
        #self.SetEndDate(2015,12,1)     # Set End Date
        self.SetEndDate(2011,9,14)     # Set End Date
        self.SetCash(100000)           # Set Strategy Cash

        # Set your Tiingo API Token here
        #Tiingo.SetAuthCode("9a596f5bd73a1470ce69bccb8cd5268db2a72780")
        Tiingo.SetAuthCode("6c44375f029af567186df2b7434dcf324688ec5b")

        resolution = Resolution.Second if self.LiveMode else Resolution.Daily
        #self.AddData(YahooFinance, "2621.T")
        #self.AddData(YahooFinance, "NDX", resolution)
        #self.AddData(YahooFinance, "NDX")
        self.ticker = self.AddEquity("QQQ", resolution)
        #self.tiingo = self.AddData(TiingoPrice, self.ticker.Symbol, resolution)
        #self.tiingo = self.AddData(YahooFinancePrice, self.ticker.Symbol, resolution)
        self.tiingo = self.AddData(TiingoPrice, self.ticker.Symbol, resolution)

        YahooFinancePrice.qa = self

    def OnData(self, data):
        self.Debug('onData')
        for kvp in data.Bars:
            symbol = kvp.Key
            value = kvp.Value
            if False:
                self.Log("OnData(Slice): {0}: {1}: {2}".format(self.Time, symbol, value.Close))
        for k, v in data.items():
            if False:
                self.Log("OnData: {0}: {1}: {2}".format(self.Time, k, v))

        t = None

        ticker = str(self.ticker)
        if data.Bars.ContainsKey(ticker):
            t = data.Bars[ticker]

        ticker = self.tiingo.Symbol
        if ticker in data:
            t = data[ticker]

        if t and not self.Portfolio.Invested:
            self.Log(t.Value)
            #if t.Close != 0 :
            #    self.Debug('Order {} {} {}'.format(self.Time, t.Symbol, t.Symbol.Value))
            #    self.Order(t.Symbol.Value, self.Portfolio.MarginRemaining / abs(t.Close + 1))
            #    self.Order(t.Symbol, self.Portfolio.MarginRemaining / abs(t.Close + 1))

json_data = '''
[
  {
    "date": "2021-01-01T00:00:00.000Z",
    "close": 27.44,
  }
]
'''

class YahooFinancePrice(PythonData):
    '''Custom Data Type: symbol from yahoo finance'''

    def __init__(self):
        self.startDates = {}
        super().__init__()

    def GetSource(self, config, date, isLiveMode):

        if isLiveMode:
            #return SubscriptionDataSource(url, SubscriptionTransportMedium.Rest)
            return None

        if not config.Symbol.Value in self.startDates:
            start_date = datetime(date.year, date.month, date.day)
            self.startDates[config.Symbol.Value] = start_date
        else:
            start_date = self.startDates[config.Symbol.Value]

        t = datetime.today()
        end_date = datetime(t.year, t.month, t.day) + timedelta(days = 1)
        
        start_seconds = int(start_date.timestamp())
        end_seconds = int(end_date.timestamp())
        url = "https://query1.finance.yahoo.com/v8/finance/chart/{}?period1={}&period2={}&interval=1d&events=div%2Csplits".format(config.Symbol.Value, start_seconds, end_seconds)
        #url = "https://query1.finance.yahoo.com/v8/finance/chart/{}?period1={}&period2={}&interval=1d".format(config.Symbol.Value, start_seconds, end_seconds)
        #YahooFinance.qa.Log(url)
        #url = "https://query1.finance.yahoo.com/v8/finance/chart/{}?period1={}interval=1d&events=div%2Csplits".format(config.Symbol.Value, start_seconds)
        return SubscriptionDataSource(url, SubscriptionTransportMedium.RemoteFile)

    def Reader(self, config, line, date, isLiveMode):
        #YahooFinance.qa.Log(date)
        yfin = YahooFinancePrice()
        yfin.Symbol = config.Symbol

        try:
            data = json.loads(line)

            tstamp = data["chart"]["result"][0]["timestamp"]
            ohlc = data["chart"]["result"][0]["indicators"]["quote"][0]
            if len(ohlc.keys()) == 0:
                return None

            items = []
            for i in range(len(tstamp)):
                item = {}
                item["date"] = datetime.fromtimestamp(tstamp[i]).isoformat() + 'Z'
                item["close"] = float(ohlc["close"][i])
                items.append(item)
            s = json.dumps(items, indent=4)
            #YahooFinancePrice.qa.Debug(s)
            tiingo = TiingoPrice()
            return tiingo.Reader(config, s, date, isLiveMode)

        except ValueError:
            # Do nothing, possible error in json decoding
            return None

