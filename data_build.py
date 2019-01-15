__author__ = 'SDee and JD'


""" This build the Information class.  Here we can """

import numpy as np
import pandas as pd
# unfortunately  quandl has sopped foworking for the free spx data so we use pandas datareader
# import quandl  # Necessary for obtaining financial data easily

import pandas_datareader.data as web
import datetime as dt

# when we import a mmodule the name ot the module will be imported from the file
# when we import a file it runs that code
from backtest import Information
import os

class DataBuild(Information):
    """Adds nnecessary indicators and other derived information to
       the trades data """

    # The initialiser gets us the indicators straight away.

    def __init__(self, symbol, bars):
        """Requires the symbol ticker and the pandas DataFrame of bars"""
        self.symbol = symbol
        self.bars = bars
        self.indicators = self.generate_indicators(DMA_days_long=200, RSI_days=14, bollinger_days=20, bollinger_deviations = 2)

    def generate_indicators(self, DMA_days_long, RSI_days, bollinger_days, bollinger_deviations):
        """Generates all indicators to expand bars dataframe
        :param DMA_days_long:
        """
    # ensures complete set of days in time series DF
    #     indicators = self.bars.asfreq('1d')

        indicators = self.bars
        indicators['Volume'] = indicators['Volume'].fillna(0)
        indicators[['Open', 'High', 'Low', 'Close', 'Adjusted Close']] = indicators[['Open', 'High', 'Low', 'Close', 'Adj Close']].ffill()
        # DMA calculation
        indicators['DMA'] = indicators['Close'].where(indicators['Close'] > 0, 0).rolling(window=DMA_days_long, center=False).mean()
        indicators['Delta'] = indicators['Close'][1:] - indicators['Close'][:-1].values
        # RSI Calculation
        indicators_trading = indicators[1:].loc[indicators['Volume'][1:] > 0, ['Close', 'Delta']]
        indicators_trading['RS_UP'] = indicators_trading['Delta'].where(indicators_trading['Delta'] > 0, 0).rolling(window=RSI_days, center=False).mean()
        indicators_trading['RS_DOWN'] = -indicators_trading['Delta'].where(indicators_trading['Delta'] <0, 0).rolling(window=RSI_days, center=False).mean()

        for i in range(RSI_days, np.size(indicators_trading.index)):    #+1 since first Delta is NaN?
            indicators_trading['RS_UP'][indicators_trading.index[i]] = (indicators_trading['RS_UP'][indicators_trading.index[i-1]]*(RSI_days -1) +
                                                  max(indicators_trading['Delta'][indicators_trading.index[i]], 0))/RSI_days
            indicators_trading['RS_DOWN'][indicators_trading.index[i]] = (indicators_trading['RS_DOWN'][indicators_trading.index[i-1]]*(RSI_days -1) -
                                                  min(indicators_trading['Delta'][indicators_trading.index[i]], 0))/RSI_days
        indicators_trading['RSI'] = 100 - (100/(1 + indicators_trading['RS_UP']/indicators_trading['RS_DOWN']))

        indicators['RSI'] = indicators_trading['RSI']

        indicators['RS_UP'] = indicators_trading['RS_UP']
        indicators['RS_DOWN'] = indicators_trading['RS_DOWN']

        # Bollinger bands

        indicators_trading['Rolling STDEV'] = indicators_trading['Close'].rolling(window=bollinger_days, center=False).std(ddof=0)

        indicators_trading['Bollinger High'] = indicators_trading['Close'].rolling(window=bollinger_days, center=False).mean() + indicators_trading['Rolling STDEV']*bollinger_deviations

        indicators_trading['Bollinger Low'] = indicators_trading['Close'].rolling(window=bollinger_days,
                                                                                   center=False).mean() - \
                                               indicators_trading['Rolling STDEV'] * bollinger_deviations

        indicators['Bollinger High'] = indicators_trading['Bollinger High']
        indicators['Bollinger Low'] = indicators_trading['Bollinger Low']
        indicators[['Bollinger High', 'Bollinger Low']] = indicators[['Bollinger High', 'Bollinger Low']].ffill()

        return indicators

# What does this __name__ == "__

# __name__ variable is __main__
# when we import a module it'll change this to the name of the file '
#  so the purpose of __name__ == "__main__" is to check whether this file is being run here or whether the code is being imported.

#  so put it all in a function then it can be called:

# df = web.DataReader('^GSPC', 'yahoo', start='1950-01-03', end='2017-09-14')
# print(df.head())

def main():

    date_start = '1984-01-01'
    date_end = '2019-01-11'
    symbol = 'SPY'

    export_path = os.getcwd() + "\\Datastore\\2019\\"
    indicators_filepath = export_path + "spy_indicators_2018.csv"

    # bars ia a pandas dataframe that we will pass

    bars = web.DataReader('^GSPC', 'yahoo', start=date_start, end=date_end)

    # bars = quandl.get('YAHOO/INDEX_GSPC', authtoken='yhwsDSnRYS6nsJN7kGAb', trim_start=date_start,
    #                  trim_end=date_end)

    print(bars.head())
    # create a csv for our own amusement
    bars.to_csv(export_path + "spy_bars.csv")
    # Create indicators
    # on instantiating our DataBuild class it automatically creates the indicators that we need in a pandas dataframe.
    infobars = DataBuild(symbol, bars)

    # we then take the indications and save it to the csv
    infobars.indicators.to_csv(indicators_filepath)

if __name__ == "__main__":
    # print("hello")
    main()

# if __name__ == "__main__":
#     # Obtain daily bars of SPY
#
#     date_start = '1984-01-01'
#     date_end = '2015-08-12'
#     symbol = 'SPY'
#
#
#     export_path = os.getcwd() + "\\Datastore\\"
#     indicators_filepath = export_path + "spy_indicators.csv"
#
#
#
#     bars = quandl.get('YAHOO/INDEX_GSPC', authtoken='yhwsDSnRYS6nsJN7kGAb', trim_start=date_start,
#                 trim_end=date_end)
#     #bars.to_csv("C:\\Users\\sdee\\Dropbox\\Praescire\\Datastore\\spy_bars.csv")
#     # Create indicators
#     infobars= DataBuild(symbol, bars)
#
#     infobars.indicators.to_csv(indicators_filepath)
#
#
#     # Create a portfolio of SPY
#     #portfolio = MarketOnOpenPortfolio(symbol, bars, signals, initial_capital=100000.0)
#     #returns = portfolio.backtest_portfolio()
#
#     #print(returns.tail(10))