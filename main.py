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
    income_statement = company.income_stmt
    prev_4_year_dates = income_statement.columns
    prev_4_year_eps_values = income_statement.loc["Diluted EPS"]

    prev_4_year_eps_map = {}
    for i in range(4):
        prev_4_year_eps_map[str(prev_4_year_dates[i]-pd.Timedelta(days=1))[:10]] = prev_4_year_eps_values.iloc[i]

    return prev_4_year_eps_map


def get_prev_4_year_prices(ticker, prev_years):
    company = yf.Ticker(ticker)
    history = company.history(period="4y")

    prev_4_year_prices_map = {}
    for year in prev_years:
        if year in history.index:
            prev_4_year_prices_map[year] = round(history.loc[year].iloc[3], 2)

    return prev_4_year_prices_map


ticker = "AAPL"

historic_eps = get_prev_4_year_eps(ticker)
historic_prices = get_prev_4_year_prices(ticker, historic_eps.keys())

for k, v in historic_prices.items():
    print(k, v)

for k, v in historic_eps.items():
    print(k, v)