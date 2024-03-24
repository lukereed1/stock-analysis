import pandas as pd
import yfinance as yf
import yahoo_fin.stock_info as si

pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 5000)


def get_ttm_fcf(ticker):
    company = yf.Ticker(ticker)
    quarterly_cash_flows = company.quarterly_cash_flow.loc["Free Cash Flow"]

    fcf = 0
    for i in range(4):
        fcf += quarterly_cash_flows.iloc[i]

    return fcf


def get_est_5yr_growth_rate(ticker):
    return si.get_analysts_info(ticker)['Growth Estimates'][ticker][4]


def get_prev_4_year_eps(ticker):
    company = yf.Ticker(ticker)
    eps = company.income_stmt.loc["Diluted EPS"]

    prev_eps = []
    for i in range(4):
        prev_eps.append(eps.iloc[i])

    return prev_eps


def

ticker = "AAPL"
get_prev_4_year_eps(ticker)