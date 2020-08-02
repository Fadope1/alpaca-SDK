import numpy as np
import requests
import talib

class stock_ins:
    BASE_URL = "https://paper-api.afrom market lpaca.markets"
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
        # this will get new bid and ask data and resize it
        bid = self.__get_bid()
        ask = self.__get_ask()

        if len(self.ask_data) >= self.save_len:
            self.ask_data.pop(self.save_len-1)
            self.bid_data.pop(self.save_len-1)

        self.bid_data.insert(0, bid)
        self.ask_data.insert(0, ask)

    def get_indicator(self, ind, *, perdiod_len=None, data=None):
        # this will return any indicator available in talib in right format
        if data is None:
            data = np.array(self.ask_data)[::-1]
        else:
            data = data[::-1]
        if perdiod_len is None:
            ind = gettatr(talib, ind)(data)
        else:
            ind = gettatr(talib, ind)(data, perdiod_len)
        return ind[::-1]

    def order(self, data):
        return requests.post("{}/v2/orders".format(self.BASE_URL), json=data, headers=self.HEADERS)

if __name__ == "__main__":
    import config
    import time

    stocks = ["DB", "TSLA", "MSFT"]
    interval = 60 # interval time in seconds: minute data=60
    save_len = 200 # length of saved prices
    Key = config.key
    sKey = config.sKey

    stock_list = []
    for stock in stocks:
        stock_list.append(stock_ins(stock, save_len, Key, sKey))

    while True:
        if market.is_open():
            start_timer = time.time()
            for stock in stock_list:
                stock.update() # this will update the bid and ask price

                data = {
                    "side": "buy",
                    "symbol": stock.stock_name,
                    "type": "market",
                    "qty": "1",
                    "time_in_force": "gtc",
                } # settings for order: order type etc.
                # print(stock.order(data)) # this will order a stock with json=data

                print(stock.ask_data[0], stock.ask_data[0], len(stock.ask_data))

            sleep_time = interval - (time.time()-start_timer)
            print("Waiting {:.2f}".format(sleep_time))
            time.sleep(sleep_time)
