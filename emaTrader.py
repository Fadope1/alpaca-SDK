import numpy as np
import requests
import datetime
import config
import market
import talib
import time
import base

stocks = ["TSLA", "NTES", "MSFT"]
interval = 60 # interval time in seconds: minute data=60
save_len = 200 # length of saved prices
Key = config.key
sKey = config.sKey

stock_list = []
for stock in stocks:
    stock_list.append(base.stock_ins(stock, save_len, Key, sKey))

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
