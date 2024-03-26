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


def get_cash_on_hand(ticker):
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    most_recent_cash_on_hand = balance_sheet.loc["Cash Cash Equivalents And Short Term Investments"].iloc[0]

    return most_recent_cash_on_hand


def get_est_5yr_growth_rate(ticker):
    return si.get_analysts_info(ticker)['Growth Estimates'][ticker][4]


def get_historic_eps(ticker):
    company = yf.Ticker(ticker)
    income_statement = company.income_stmt
    prev_4_year_dates = income_statement.columns
    prev_4_year_eps_values = income_statement.loc["Diluted EPS"]

    prev_4_year_eps_map = {}
    for i in range(4):
        prev_4_year_eps_map[str(prev_4_year_dates[i] - pd.Timedelta(days=2))[:10]] = prev_4_year_eps_values.iloc[i]

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

    for i in range(len(prices)):
        pe_ratio = round(prices[i] / eps[i], 2)
        prev_4_year_pe_ratio[dates[i]] = pe_ratio

    return prev_4_year_pe_ratio


def get_future_cash_flows(ticker, years, growth_rate):
    cash_flow = get_ttm_fcf(ticker)
    future_cash_flows = []
    print(f"Initial Cash Flow: {cash_flow}")
    for i in range(years):
        cash_flow = cash_flow * (1 + growth_rate)
        future_cash_flows.append(round(cash_flow, 2))

    return future_cash_flows


def get_discounted_rates(fcf, discount_rate=0.15):
    yearly_discounted_amounts = []

    j = 1
    for i in range(len(fcf)):
        discounted_amount = fcf[i] / (1 + discount_rate) ** j
        yearly_discounted_amounts.append(round(discounted_amount, 2))
        j += 1

    return yearly_discounted_amounts


def get_4_year_pe_average(historic_pe):
    pe_sum = 0

    for v in historic_pe:
        pe_sum += v

    return round(pe_sum / len(historic_pe), 2)


def get_terminal_value(ticker, historic_pe_average, year_10_fcf):
    multiplier = get_terminal_value_multiplier(ticker, historic_pe_average)
    print(f"MULTIPLIER: {multiplier}")
    print(f"YEAR 10 FCF: {year_10_fcf}")
    return round(multiplier * year_10_fcf, 2)


def get_terminal_value_multiplier(ticker, historic_pe_avg):
    est_growth_rate = float(get_est_5yr_growth_rate(ticker)[:-2])
    print(f"EST GROWTH RATE: {est_growth_rate*2}")
    return abs(min(est_growth_rate * 2, historic_pe_avg))


def get_terminal_discount_value(terminal_value, years, discount_rate=0.15):
    discounted_value = terminal_value / (1 + discount_rate) ** years

    return round(discounted_value, 2)


def sum_all_discounted_values(yearly_discounted_values, terminal_value_discounted):
    discounted_cash_flow_values = sum(yearly_discounted_values) + terminal_value_discounted

    return discounted_cash_flow_values


def add_margin_of_safety(intrinsic_value, mos_rate):
    return intrinsic_value * (1 - mos_rate)


def convert_to_billions(value):
    return round(value / 1000000000, 2)


def discounted_cash_flow_analysis(company, years, estimated_growth, mos_rate):
    future_cash_flows = get_future_cash_flows(company, years, estimated_growth)
    future_values_discounted = get_discounted_rates(future_cash_flows)
    print(f"FUTURE CASH FLOWS: {future_cash_flows}")
    print(f"FUTURE DISCOUNT RATES: {future_values_discounted}")

    historic_eps_map = get_historic_eps(company)
    historic_prices_map = get_historic_prices(company, list(historic_eps_map.keys()))

    eps = list(historic_eps_map.values())
    dates = list(historic_eps_map.keys())
    prices = list(historic_prices_map.values())
    print(f"EPS: {eps}")
    print(f"DATES: {dates}")
    print(f"PRICES: {prices}")

    historic_pe = get_historic_pe_ratio(dates, eps, prices)
    historic_pe_values = list(historic_pe.values())
    print(f"PE RATIOS: {historic_pe_values}")
    pe_4_year_average = get_4_year_pe_average(historic_pe_values)

    terminal_value = get_terminal_value(company, pe_4_year_average, future_cash_flows[len(future_cash_flows) - 1])
    print(f"TERMINAL VALUE: {terminal_value}")

    terminal_value_discounted = get_terminal_discount_value(terminal_value, years)
    print(f"TERMINAL VALUE DISCOUNTED: {terminal_value_discounted}")

    discounted_cash_flow_total = sum_all_discounted_values(future_values_discounted, terminal_value_discounted)
    print(f"INTRINSIC VALUE LESS CASH: {discounted_cash_flow_total}")

    cash_on_hand = get_cash_on_hand(company)

    intrinsic_value = cash_on_hand + discounted_cash_flow_total
    print(f"INTRINSIC VALUE PLUS CASH: {convert_to_billions(intrinsic_value)}B")

    buy_value = add_margin_of_safety(intrinsic_value, mos_rate)
    print(f"BUY RANGE INCLUDING MARGIN OF SAFETY: {buy_value}")


discounted_cash_flow_analysis("AAPL", 10, 0.12, 0.25)

