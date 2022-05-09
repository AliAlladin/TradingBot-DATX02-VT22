import alpaca_trade_api as tradeapi
import pandas as pd
import time
from Alpaca.Config2 import *


class AlpacaBroker:
    """
    Wrapper class for the alpaca_trade_api library.
    """

    def __init__(self):
        """
        Constructor for the class.
        """
        self.api = tradeapi.REST(
            ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')
        self.error = tradeapi.rest.APIError

    def market_is_open(self) -> bool:
        """
        Function that checks if market is open.
        :return: True if market is open, otherwise False.
        """
        clock = self.api.get_clock()
        return clock.is_open and (clock.next_close - clock.timestamp).total_seconds() > 120

    def wait_for_market_open(self) -> None:
        """
        Puts the programme to sleep if the market is not open.
        :return: None
        """
        clock = self.api.get_clock()
        if not clock.is_open:
            print("Going to sleep!")
            time_to_open = (clock.next_open - clock.timestamp).total_seconds()
            time.sleep(round(time_to_open))

    def buy(self, symbol: str, target_position_size: float) -> str:
        """
        Function to place a buy order.
        :param symbol: Symbol of stock to be bought.
        :param target_position_size: Number of stocks to be bought.
        :return: Id of the placed order.
        """
        try:
            order = self.api.submit_order(
                symbol, target_position_size, "buy", "market", "day")

            return order.id
        except Exception as e:
            print(e)

    def sell(self, symbol: str, target_position_size: float) -> str:
        """
        Function to place a sell order.
        :param symbol: Symbol of stock to be sold.
        :param target_position_size: Number of stocks to be sold.
        :return: Id of the placed order.
        """
        try:
            order = self.api.submit_order(symbol, target_position_size, "sell", "market", "day")
            return order.id
        except Exception as e:
            print(e)

    def get_order(self, order_id: str) -> dict:
        """
        Returns order information given order id.
        :param order_id: Id of the order.
        :return: Dictonary with order information.
        """
        order = self.api.get_order(order_id)

        order_info = {
            'id': order.id,
            'symbol': order.symbol,
            'type': order.side,
            'qty': float(order.qty),
            'filled_at': order.filled_at
        }

        return order_info

    def all_orders(self) -> [dict]:
        """
        Returns a list of all open orders.
        :return: List of dictionaries with order information.
        """
        orders = self.api.list_orders(limit=500)
        order_list = []
        for order in orders:
            order_info = {
                'id': order.id,
                'symbol': order.symbol,
                'type': order.side,
                'qty': float(order.qty),
                'time_stamp': order.created_at
            }
            order_list.append(order_info)
        return pd.DataFrame(order_list)

    def get_position(self, symbol: str) -> dict:
        """
        Returns position in a stock given ticker symbol.
        :param symbol: Symbol of the stock.
        :return: A dictonary with position information.
        """
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

    def get_all_postions(self) -> [dict]:
        """
        Returns a list of all current positions.
        :return: A list of all current positions.
        """
        positions = self.api.list_positions()
        position_list = []
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
            position_list.append(position_info)
        return pd.DataFrame(position_list)

    def get_balance(self) -> float:
        """
        Gets account balance
        :return: Account balance.
        """
        return float(self.api.get_account().cash)

    def get_portfolio_value(self) -> float:
        """
        Gets portfolio value.
        :return: Portfolio value.
        """
        return float(self.api.get_account().equity)

    def get_shortable(self, pairs: pd.DataFrame) -> None:
        """
        Filters out non-shortable stocks given a dataframe of pairs.
        :param pairs: DataFrame with all pairs.
        :return: None
        """
        for index, row in pairs.iterrows():
            try:
                if not self.api.get_asset(row[0]).shortable or not self.api.get_asset(row[1]).shortable:
                    pairs.drop(index, inplace=True)
            except Exception as e:
                print(e)
        pairs.reset_index(drop=True, inplace=True)
