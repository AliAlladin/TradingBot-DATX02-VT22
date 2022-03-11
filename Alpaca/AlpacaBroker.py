from datetime import datetime
from alpaca_trade_api import REST
import time
import pandas as pd
from Config import *


class AlpacaBroker:
    def __init__(self):
        self.api = REST(
            ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')

    def get_balance(self):
        return float(self.api.get_account().cash)

    def get_portfolio_value(self):
        return float(self.api.get_account().equity)

    # Function that checks if market is open.
    def market_is_open(self):
        clock = self.api.get_clock()
        return clock.is_open and (clock.next_close - clock.timestamp).total_seconds() > 120

    def wait_for_market_open(self):
        clock = self.api.get_clock()
        if not clock.is_open:
            print("Going to sleep!")
            time_to_open = (clock.next_open - clock.timestamp).total_seconds()
            time.sleep(round(time_to_open))

    # Function to place a buy order.
    def buy(self, symbol: str, target_position_size: float, limit_price: float):
        order = self.api.submit_order(
            symbol, target_position_size, "buy", "limit", "day", limit_price)
        print("BUY order for {} {} at {}$ {}".format(order.qty,
              order.symbol, order.limit_price, order.status))

        order_info = {
            'id': order.id,
            'symbol': order.symbol,
            'type': order.side,
            'qty': float(order.qty),
            'time_stamp': order.created_at
        }
        return order_info

    # Function to place a sell order.
    def sell(self, symbol: str, target_position_size: float, limit_price: float):
        order = self.api.submit_order(
            symbol, target_position_size, "sell", "limit", "day", limit_price)
        print("SELL order for {} {} at {}$ {}".format(order.qty,
              order.symbol, order.limit_price, order.status))

        order_info = {
            'id': order.id,
            'symbol': order.symbol,
            'type': order.side,
            'qty': float(order.qty),
            'time_stamp': order.created_at
        }
        return order_info

    def get_all_orders(self):
        orders = self.api.list_orders(limit=500)
        list = []
        for order in orders:
            order_info = {
                'id': order.id,
                'symbol': order.symbol,
                'type': order.side,
                'qty': float(order.qty),
                'time_stamp': order.created_at
            }
            list.append(order_info)
        return pd.DataFrame(list)


broker = AlpacaBroker()

print(broker.get_all_orders())
