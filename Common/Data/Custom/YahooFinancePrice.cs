﻿/*
 * QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
 * Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*/

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using Newtonsoft.Json;
using NodaTime;
using QuantConnect.Data.Market;
using QuantConnect.Data.UniverseSelection;
using static QuantConnect.StringExtensions;
using QuantConnect.Data.Custom.Tiingo;
using Newtonsoft.Json.Linq;
using QuantConnect.Logging;

namespace QuantConnect.Data.Custom.YahooFinance
{
    /// <summary>
    /// Tiingo daily price data
    /// https://api.tiingo.com/docs/tiingo/daily
    /// </summary>
    /// <remarks>Requires setting <see cref="Tiingo.AuthCode"/></remarks>
    public class YahooFinancePrice : TiingoPrice
    {
        private readonly ConcurrentDictionary<string, DateTime> _startDates = new ConcurrentDictionary<string, DateTime>();

        /// <summary>
        /// Initializes an instance of the <see cref="YahooFinancePrice"/> class.
        /// </summary>
        public YahooFinancePrice()
        {
            Symbol = Symbol.Empty;
            DataType = MarketDataType.Base;
        }

        /// <summary>
        /// Return the URL string source of the file. This will be converted to a stream
        /// </summary>
        /// <param name="config">Configuration object</param>
        /// <param name="date">Date of this source file</param>
        /// <param name="isLiveMode">true if we're in live mode, false for backtesting mode</param>
        /// <returns>String URL of source file.</returns>
        public override SubscriptionDataSource GetSource(SubscriptionDataConfig config, DateTime date, bool isLiveMode)
        {
            DateTime startDate;
            if (!_startDates.TryGetValue(config.Symbol.Value, out startDate))
            {
                startDate = date;
                _startDates.TryAdd(config.Symbol.Value, startDate);
            }

            var startSeconds = new DateTimeOffset(startDate).ToUnixTimeSeconds();
            var endSeconds = new DateTimeOffset(DateTime.Today).AddDays(1).ToUnixTimeSeconds();
            String symbol = config.Symbol.Value;
            if (symbol.EndsWith('$')) {
                startSeconds = 7223400;
                symbol = symbol.Trim('$');
            }
            var source = Invariant($"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={startSeconds}&period2={endSeconds}&interval=1d&events=div%2Csplits");
            //Log.Trace(source);
            return new SubscriptionDataSource(source, SubscriptionTransportMedium.RemoteFile, FileFormat.UnfoldingCollection);
        }

        /// <summary>
        ///     Reader converts each line of the data source into BaseData objects. Each data type creates its own factory method,
        ///     and returns a new instance of the object
        ///     each time it is called. The returned object is assumed to be time stamped in the config.ExchangeTimeZone.
        /// </summary>
        /// <param name="config">Subscription data config setup object</param>
        /// <param name="content">Content of the source document</param>
        /// <param name="date">Date of the requested data</param>
        /// <param name="isLiveMode">true if we're in live mode, false for backtesting mode</param>
        /// <returns>
        ///     Instance of the T:BaseData object generated by this line of the CSV
        /// </returns>
        public override BaseData Reader(SubscriptionDataConfig config, string content, DateTime date, bool isLiveMode)
        {
           	dynamic data = Newtonsoft.Json.JsonConvert.DeserializeObject(content);
            List<YahooFinancePrice> list = new List<YahooFinancePrice>();

            var tstamp = data["chart"]["result"][0]["timestamp"];
            var ohlc = data["chart"]["result"][0]["indicators"]["quote"][0];
            var adjclose = data["chart"]["result"][0]["indicators"]["adjclose"][0];
            int c_tstamp = ((JArray)tstamp).Count;
            int c_ohlc = ((JArray)ohlc["close"]).Count;
            if (tstamp == null || ohlc == null || c_tstamp != c_ohlc) {
                return null;
            }

            for (int i = 0; i < c_tstamp; i++) {
                var item = new YahooFinancePrice();
                item.Date = DateTimeOffset.FromUnixTimeSeconds((long)tstamp[i]).DateTime;
                item.Open = (decimal)ohlc["open"][i];
                item.High = (decimal)ohlc["high"][i];
                item.Low = (decimal)ohlc["low"][i];
                item.Close = (decimal)ohlc["close"][i];
                item.AdjustedClose = (decimal)adjclose["adjclose"][i];
                item.Symbol = config.Symbol;
                item.Time = item.Date;
                item.Value = item.Close;
                list.Add(item);
            }

            return new BaseDataCollection(date, config.Symbol, list);
        }
    }
}
