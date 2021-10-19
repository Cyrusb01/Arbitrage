import ccxt

exchange = ccxt.kraken()


symbols = ["BTC/USD"]


for i in symbols:
    ohlc = exchange.fetch_ohlcv(i, timeframe = '1d')
    print(ohlc[-1])
    # for candle in ohlc:
    #     print(candle)


# eth_ticker = exchange.fetch_ticker('ETH/USDT')

# print(eth_ticker['baseVolume'])
# for i in eth_ticker:
#     print(i, ':', eth_ticker[i])
# # for candle in ohlc:
# #     print(candle)