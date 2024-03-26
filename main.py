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


def get_historic_eps(ticker):
    company = yf.Ticker(ticker)
    income_statement = company.income_stmt
    prev_4_year_dates = income_statement.columns
    prev_4_year_eps_values = income_statement.loc["Diluted EPS"]

    prev_4_year_eps_map = {}
    for i in range(4):
        prev_4_year_eps_map[str(prev_4_year_dates[i] - pd.Timedelta(days=1))[:10]] = prev_4_year_eps_values.iloc[i]

    return prev_4_year_eps_map


def get_historic_prices(ticker, prev_years):
    company = yf.Ticker(ticker)
    history = company.history(period="4y")

    prev_4_year_prices_map = {}
    for year in prev_years:
        if year in history.index:
            prev_4_year_prices_map[year] = round(history.loc[year].iloc[3], 2)

    return prev_4_year_prices_map


def get_historic_pe_ratio(dates, eps, prices):
    prev_4_year_pe_ratio = {}

    for i in range(4):
        pe_ratio = round(prices[i] / eps[i], 2)
        prev_4_year_pe_ratio[dates[i]] = pe_ratio

    return prev_4_year_pe_ratio


def get_future_cash_flows(ticker, years, growth_rate):
    cash_flow = 69495
    future_cash_flows = []

    for i in range(years):
        cash_flow = cash_flow * (1 + growth_rate)
        future_cash_flows.append(round(cash_flow, 2))

    return future_cash_flows


def get_discount_rates(fcf, discount_rate=0.15):
    yearly_discounted_amounts = []

    j = 1
    for i in range(len(fcf)):
        discounted_amount = fcf[i] / (1 + discount_rate) ** j
        yearly_discounted_amounts.append(round(discounted_amount, 2))
        j += 1

    return yearly_discounted_amounts




company = "AAPL"


future_cash_flows = get_future_cash_flows(company, 10, 0.12)
future_discount_rates = get_discount_rates(future_cash_flows)

print(future_cash_flows)
print(future_discount_rates)