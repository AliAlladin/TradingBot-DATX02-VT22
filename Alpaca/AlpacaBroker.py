from datetime import datetime
from turtle import pos
import alpaca_trade_api as tradeapi
import time
import pandas as pd
from Config import *


class AlpacaBroker:
    def __init__(self):
        self.api = tradeapi.REST(
            ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')
        self.error = tradeapi.rest.APIError

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
        try:
            if target_position_size * limit_price <= self.get_balance:
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
            else:
                print("Can't create BUY order. (Check available balance)")
        except self.error:
            print("BUY ERROR")

    # Function to place a sell order.
    def sell(self, symbol: str, target_position_size: float, limit_price: float):
        try:
            position = self.get_position(symbol)
            if position is not None and target_position_size <= position["qty"]:
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
            else:
                print("Can't create SELL order. (Check symbol and target_position_size)")
        except self.error:
            print("SELL ERROR")

    def get_orders(self, symbol: str):
        all_orders = self.all_orders()
        return all_orders[all_orders['symbol'] == symbol]

    def all_orders(self):
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

    def get_position(self, symbol: str):
        try:
            position = self.api.get_position(symbol=symbol)
            position_info = {
                'id': position.asset_id,
                'symbol': position.symbol,
                'qty': float(position.qty),
                'avg_entry_price': float(position.avg_entry_price),
                'current_price': float(position.current_price),
                'change': (float(position.current_price) / float(position.avg_entry_price)) - 1,
                'market_value': float(position.market_value)
            }
            return position_info
        except self.error:
            print("Position does not exist")

    def all_postions(self):
        positions = self.api.list_positions()
        list = []
        for position in positions:
            position_info = {
                'id': position.asset_id,
                'symbol': position.symbol,
                'qty': float(position.qty),
                'avg_entry_price': float(position.avg_entry_price),
                'current_price': float(position.current_price),
                'change': (float(position.current_price) / float(position.avg_entry_price)) - 1,
                'market_value': float(position.market_value)
            }
            list.append(position_info)
        return pd.DataFrame(list)


broker = AlpacaBroker()

print(broker.get_position("AAPL"))
print(broker.get_orders("AAPL"))
