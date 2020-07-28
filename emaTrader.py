import market
import numpy as np
import requests
import datetime
import config
import talib
import time

stocks = ["TSLA", "NTES", "MSFT"]
interval = 60 # interval time in seconds: minute data=60
save_len = 200 # length of saved prices
Key = config.key
sKey = config.sKey

class _stock_ins:
    BASE_URL = "https://paper-api.alpaca.markets"
    DATA_URL = "https://data.alpaca.markets"

    def __init__(self, stock_name, save_len, api_key, secret_key):
        self.stock_name = stock_name
        self.save_len = save_len
        self.ask_data = []
        self.bid_data = []

        self.HEADERS = {'APCA-API-KEY-ID': api_key, 'APCA-API-SECRET-KEY': secret_key}

    def __get_bid(self):
        return requests.get("{}/v1/last/stocks/{}".format(self.DATA_URL, self.stock_name), headers=self.HEADERS).json()["last"]["price"]

    def __get_ask(self):
        return requests.get("{}/v1/last_quote/stocks/{}".format(self.DATA_URL, self.stock_name), headers=self.HEADERS).json()["last"]["askprice"]

    def update(self):
        bid = float(self.__get_bid())
        ask = float(self.__get_ask())

        if len(self.ask_data) >= self.save_len:
            self.ask_data.pop(self.save_len-1)
            self.bid_data.pop(self.save_len-1)

        self.bid_data.insert(0, bid)
        self.ask_data.insert(0, ask)

    def get_indicator(self, ind, *, perdiod_len=None, data=None):
        if data is None:
            data = np.array(self.ask_data)[::-1]
        else:
            data = data[::-1]
        if perdiod_len is None:
            ind = getattr(talib, ind)(data)
        else:
            ind = getattr(talib, ind)(data, perdiod_len)
        return ind[::-1]

    def order(self, data):
        '''   example data
        data = {
            "side": "buy/sell",
            "symbol": self.stock_name,
            "type": "market",
            "qty": "0-...",
            "time_in_force": "gtc",
            "order_class": "bracket",
            "take_profit": {
              "limit_price": "301"
            },
            "stop_loss": {
              "stop_price": "299",
              "limit_price": "298.5"
            }
            }

        '''
        return requests.post("{}/v2/orders".format(self.BASE_URL), json=data, headers=self.HEADERS)

stock_list = []
for stock in stocks:
    stock_list.append(_stock_ins(stock, save_len, Key, sKey))

while True:
    if market.is_open():
        start_timer = time.time()
        for stock in stock_list:
            stock.update() # this will update the bid and ask price

            if len(stock.ask_data) >= save_len:
                ema200 = stock.get_indicator(ind="EMA", perdiod_len=save_len)

                current_price = stock.ask_data[0]
                last_price = stock.ask_data[-5]
                current_ema = ema200[0]
                last_ema = ema200[-5]

                print("Current price: {} | current ema: {}".format(current_price, current_ema))

                data = {
                    "side": None,
                    "symbol": stock.stock_name,
                    "type": "market",
                    "qty": "1",
                    "time_in_force": "gtc",
                }

                if last_ema < last_price:
                    if current_ema > current_price:
                        # buy
                        data["side"] = "buy"
                elif last_ema > last_price:
                    if current_ema < current_price:
                        # sell
                        data["side"] = "sell"

                if data["side"] is not None:
                    stock.order(data)

        sleep_time = interval - (time.time()-start_timer)
        print("Waiting {:.2f}".format(sleep_time))
        time.sleep(sleep_time)
