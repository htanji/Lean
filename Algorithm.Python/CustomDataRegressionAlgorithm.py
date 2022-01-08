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
    klass = None

    def Initialize(self):

        self.SetStartDate(2011,9,13)   # Set Start Date
        #self.SetEndDate(2015,12,1)     # Set End Date
        self.SetEndDate(2012,9,14)     # Set End Date
        self.SetCash(100000)           # Set Strategy Cash

        resolution = Resolution.Second if self.LiveMode else Resolution.Daily
        #self.AddData(YahooFinance, "2621.T", resolution)
        #self.AddData(YahooFinance, "NDX", resolution)
        self.AddData(YahooFinance, "NDX")
        CustomDataRegressionAlgorithm.klass = self

    def OnData(self, data):
        self.Debug('onData' + data['NDX'])
        if not self.Portfolio.Invested:
            if data['NDX'].Close != 0 :
                self.Order('NDX', self.Portfolio.MarginRemaining / abs(data['NDX'].Close + 1))


class YahooFinance(PythonData):
    '''Custom Data Type: symbol from yahoo finance'''

    def GetSource(self, config, date, isLiveMode):
        #CustomDataRegressionAlgorithm.klass.Debug('date: {}'.format(date))
        #url = "https://query1.finance.yahoo.com/v8/finance/chart/NDX?period1=1638576000&period2=1640822400&interval=1d&events=div%2Csplits"
        url = "https://query1.finance.yahoo.com/v8/finance/chart/{}?period1={}&period2={}&interval=1d&events=div%2Csplits".format(config.Symbol.Value, int(date.timestamp()), int((date + timedelta(days=1)).timestamp()))

        if isLiveMode:
            return SubscriptionDataSource(url, SubscriptionTransportMedium.Rest)

        #return "http://my-ftp-server.com/futures-data-" + date.ToString("Ymd") + ".zip"
        # OR simply return a fixed small data file. Large files will slow down your backtest
        #return SubscriptionDataSource(url, SubscriptionTransportMedium.Rest)
        return SubscriptionDataSource(url, SubscriptionTransportMedium.RemoteFile)

    

    def Reader(self, config, line, date, isLiveMode):
        yfin = YahooFinance()
        yfin.Symbol = config.Symbol

        try:
            data = json.loads(line)
            ohlc = data["chart"]["result"][0]["indicators"]["quote"][0]
            if len(ohlc.keys()) == 0:
                return None

            yfin["Open"] = float(ohlc["open"][0])
            yfin["High"] = float(ohlc["high"][0])
            yfin["Low"] = float(ohlc["low"][0])
            yfin["Close"] = float(ohlc["close"][0])
            yfin["Volume"] = float(ohlc["volume"][0])

            #yfin.Time = datetime.strptime(data[0], "%Y-%m-%d")
            yfin.Time = date
            yfin.EndTime = date + timedelta(days=1)
            yfin.Value = yfin["Close"]

            CustomDataRegressionAlgorithm.klass.Debug('date: {}'.format(date))
            CustomDataRegressionAlgorithm.klass.Debug('Open: {}'.format(yfin["Open"]))
            CustomDataRegressionAlgorithm.klass.Debug(yfin.Time)
            CustomDataRegressionAlgorithm.klass.Debug(yfin.EndTime)
            CustomDataRegressionAlgorithm.klass.Debug('{} {}'.format(type(yfin.Time), type(yfin.EndTime)))
            return yfin
        except ValueError:
            # Do nothing, possible error in json decoding
            return None

