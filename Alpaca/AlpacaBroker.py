import time
import alpaca_trade_api as tradeapi
import pandas as pd
from Alpaca.Config import *

'''
Wrapper class for the alpaca_trade_api library. 
'''
class AlpacaBroker:
    def __init__(self):
        self.api = tradeapi.REST(
            ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')
        self.error = tradeapi.rest.APIError

    '''
    Function that checks if market is open.
    '''
    def market_is_open(self):
        clock = self.api.get_clock()
        return clock.is_open and (clock.next_close - clock.timestamp).total_seconds() > 120

    '''
    Puts the programme to sleep if the market is not open.
    '''
    def wait_for_market_open(self):
        clock = self.api.get_clock()
        if not clock.is_open:
            print("Going to sleep!")
            time_to_open = (clock.next_open - clock.timestamp).total_seconds()
            time.sleep(round(time_to_open))

    '''
    Function to place a buy order.
    '''
    def buy(self, symbol: str, target_position_size: float):
        try:
            order = self.api.submit_order(
                symbol, target_position_size, "buy", "market", "day")

            return order.id
        except Exception as e:
            print(e)
    '''
    Function to place a sell order.
    '''
    def sell(self, symbol: str, target_position_size: float):
        try:
            order = self.api.submit_order(symbol, target_position_size, "sell", "market", "day")
            return order.id
        except Exception as e:
            print(e)

    '''
    Returns order information given order id.
    '''
    def get_order(self, id: str):
        order = self.api.get_order(id)

        order_info = {
            'id': order.id,
            'symbol': order.symbol,
            'type': order.side,
            'qty': float(order.qty),
            'filled_at': order.filled_at
        }

        return order_info

    '''
    Returns a list of all open orders.
    '''
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

    '''
    Returns position in a stock given ticker symbol.
    '''
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
        except Exception as e:
            print(e)
            return {}

    '''
    Returns a list of all current positions in the stocks. 
    '''
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

    '''
    Returns account balance.
    '''
    def get_balance(self):
        return float(self.api.get_account().cash)

    '''
    Returns portfolio value.
    '''
    def get_portfolio_value(self):
        return float(self.api.get_account().equity)

    '''
    Filters out non-shortable stocks given a dataframe of pairs.
    '''
    def get_shortable(self, pairs: pd.DataFrame):
        for index, row in pairs.iterrows():
            try:
                if not self.api.get_asset(row[0]).shortable or not self.api.get_asset(row[1]).shortable:
                    pairs.drop(index, inplace=True)
            except Exception as e:
                print(e)
        pairs.reset_index(drop=True, inplace=True)
