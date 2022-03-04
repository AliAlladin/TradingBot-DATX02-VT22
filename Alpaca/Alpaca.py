import alpaca_trade_api as tradeapi
from Config import *


class Alpaca:
    def __init__(self):
        self.api = tradeapi.REST(
            ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')

    def getBalance(self):
        return float(self.api.get_account().cash)
