from util import get_soup


def get_income_statement(ticker):
    url = f"https://stockanalysis.com/stocks/{ticker}/financials/"
    income_statement = get_soup(url)
    return income_statement


def get_ttm_income_statement(ticker):
    url = f"https://stockanalysis.com/stocks/{ticker}/financials/?p=trailing"
    quarterly_income_statement = get_soup(url)
    return quarterly_income_statement


def get_balance_sheet(ticker):
    url = f"https://stockanalysis.com/stocks/{ticker}/financials/balance-sheet/"
    balance_sheet = get_soup(url)
    return balance_sheet


def get_sales_growth_rates(income_statement, years):
    try:
        gross_profits = income_statement.find("span", string="Gross Profit").parent.parent
        year_columns = gross_profits.find_all("td")
    except AttributeError:
        print("There was a problem finding Gross Profits")
        return

    historic_profits = get_historic_growth_data_from_rows(year_columns, years)
    display_growth_rates(historic_profits, years)


def get_eps_growth_rates(income_statement, years):
    try:
        eps = income_statement.find("span", string="EPS (Diluted)").parent.parent
        year_columns = eps.find_all("td")
    except AttributeError:
        print("There was a problem finding EPS")
        return

    historic_eps = get_historic_growth_data_from_rows(year_columns, years)
    display_growth_rates(historic_eps, years)


def get_free_cash_flow_growth_rates(income_statement, years):
    try:
        fcf = income_statement.find("span", string="Free Cash Flow").parent.parent
        year_columns = fcf.find_all("td")
    except AttributeError:
        print("There was a problem finding Free Cash Flow")
        return

    historic_fcf = get_historic_growth_data_from_rows(year_columns, years)
    display_growth_rates(historic_fcf, years)


def get_equity_growth_rates(balance_sheet, years):
    try:
        equity = balance_sheet.find("span", string="Shareholders' Equity").parent.parent
        year_columns = equity.find_all("td")
    except AttributeError:
        print("There was a problem finding Equity values")
        return

    historic_equity = get_historic_growth_data_from_rows(year_columns, years)
    display_growth_rates(historic_equity, years)


def get_historic_growth_data_from_rows(data_columns, years):
    historic_data = []
    for i in range(1, years + 1):
        data = data_columns[i].text
        if data == "-":
            historic_data.append(0)
        else:
            data = data.replace(",", "")
            historic_data.append(float(data))
    return historic_data


def calculate_growth_rate(time_frame_in_years, start_amount, end_amount):
    if start_amount == 0:
        return "N/A"
    growth_rate = (end_amount / start_amount) ** (1 / time_frame_in_years) - 1
    if isinstance(growth_rate, complex):
        return "N/A"
    growth_rate = round(growth_rate * 100, 2)
    return growth_rate


def display_growth_rates(historic_data, years):
    latest = historic_data[0]
    initial_amount = historic_data[len(historic_data) - 1]
    if years == 10:
        ten_year_growth_rate = calculate_growth_rate(10, initial_amount, latest)
        print(f"10 year Growth Rate: {ten_year_growth_rate}%")
    else:
        max_growth_rate = calculate_growth_rate(years, initial_amount, latest)
        print(f"{years} year Growth Rate: {max_growth_rate}%")

    if years >= 5:
        five_year_growth_rate = calculate_growth_rate(5, historic_data[4], latest)
        print(f"5 year Growth Rate: {five_year_growth_rate}%")

    one_year_growth_rate = calculate_growth_rate(2, historic_data[1], latest)
    print(f"1 year Growth Rate: {one_year_growth_rate}%")