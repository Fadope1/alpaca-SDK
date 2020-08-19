import baseStrategy
import config
import market
import time

stocks = ["TSLA", "NTES", "MSFT"]
interval = 60 # interval time in seconds: minute data=60
period_len = 200 # indicator length
last_nr = 2 # last nr to compare current stats
save_len = period_len + last_nr
Key = config.key
sKey = config.sKey

stock_list = []
for stock in stocks:
    stock_list.append(baseStrategy.stock_ins(stock, save_len, Key, sKey))

data = {
    "side": None,
    "symbol": None,
    "type": "market",
    "qty": "1",
    "time_in_force": "gtc",
}

while True:
    if market.is_open():
        start_timer = time.time()
        for stock in stock_list:
            stock.update() # this will update the bid and ask price

            if len(stock.ask_data) >= save_len:
                ema200 = stock.get_indicator(ind="EMA", perdiod_len=period_len)

                current_price = stock.ask_data[0]
                last_price = stock.ask_data[last_nr]
                current_ema = ema200[0]
                last_ema = ema200[last_nr]

                print("Current price: {} | Current ema: {}".format(current_price, current_ema))
                print("Last price: {} | Last ema: {}".format(last_price, last_ema))

                data["side"] = None
                data["symbol"] = stock.stock_name

                if last_ema < last_price:
                    if current_ema > current_price:
                        # buy
                        data["side"] = "buy"
                        print("buying")
                elif last_ema > last_price:
                    if current_ema < current_price:
                        # sell
                        data["side"] = "sell"
                        print("selling")

                if data["side"] is not None:
                    stock.order(data)

        sleep_time = interval - (time.time()-start_timer)
        print("Waiting {:.2f}".format(sleep_time))
        time.sleep(sleep_time)
