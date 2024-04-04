from bs4 import BeautifulSoup
import yahoo_fin.stock_info as si
import requests


def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, "html.parser")


def get_years_available(soup):
    years = len(soup.find_all("th", {"class": "border-b"}))
    #  Removes columns that don't reflect a certain year
    if years > 11:
        years -= 2
    else:
        years -= 1
    return years


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


def get_ratios_and_metrics(ticker):
    url = f"https://stockanalysis.com/stocks/{ticker}/financials/ratios/"
    ratios_and_metrics = get_soup(url)
    return ratios_and_metrics


def get_analyst_5_year_growth_prediction(ticker):
    try:
        rate = si.get_analysts_info(ticker)['Growth Estimates'][ticker][4]
        return rate
    except AttributeError:
        return "Problem finding analyst growth rate estimate"


def get_growth_rate(time_frame_in_years, start_amount, end_amount):
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
        ten_year_growth_rate = get_growth_rate(10, initial_amount, latest)
        print(f"10 year Growth Rate: {ten_year_growth_rate}%")
    else:
        max_growth_rate = get_growth_rate(years, initial_amount, latest)
        print(f"{years} year Growth Rate: {max_growth_rate}%")

    if years >= 5:
        five_year_growth_rate = get_growth_rate(5, historic_data[4], latest)
        print(f"5 year Growth Rate: {five_year_growth_rate}%")

    one_year_growth_rate = get_growth_rate(2, historic_data[1], latest)
    print(f"1 year Growth Rate: {one_year_growth_rate}%")


def display_metrics(metric, historic_data, years):
    if historic_data is None:
        return
    max_years_average = round(sum(historic_data[1:]) / years, 2)
    print(f"{years} year {metric} Average: {max_years_average}")

    if years >= 5:
        five_year_average = round(sum(historic_data[1:6]) / 5, 2)
        print(f"5 year {metric} Average: {five_year_average}")

    ttm = historic_data[0]
    print(f"TTM {metric}: {ttm}")


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


def get_historic_ratio_data_from_rows(data_columns, years):
    historic_data = []
    try:
        for i in range(1, years + 2):
            data = data_columns[i].text
            if data == "-":
                historic_data.append(0)
            else:
                data = data.replace("%", "")
                historic_data.append(float(data))
        return historic_data
    except IndexError:
        print("There was a problem finding this metric")


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


def get_roic(ratios, years):
    try:
        roic = ratios.find("span", string="Return on Capital (ROIC)").parent.parent
        year_columns = roic.find_all("td")
    except AttributeError:
        print("There was a problem finding this ratio")
        return

    historic_roic = get_historic_ratio_data_from_rows(year_columns, years)
    display_metrics("ROIC", historic_roic, years)


def get_pe_ratio(ratios, years):
    try:
        pe = ratios.find("span", string="PE Ratio").parent.parent
        year_columns = pe.find_all("td")
    except AttributeError:
        print("There was a problem finding PE Ratios")
        return

    historic_pe = get_historic_ratio_data_from_rows(year_columns, years)
    display_metrics("PE Ratio", historic_pe, years)


def get_debt_fcf_ratio(ratios, years):
    try:
        debt_fcf = ratios.find("span", string="Debt / FCF Ratio").parent.parent
        year_columns = debt_fcf.find_all("td")
    except AttributeError:
        print("There was a problem getting Debt/FCF Ratios")
        return

    historic_debt_fcf = get_historic_ratio_data_from_rows(year_columns, years)
    display_metrics("Debt/FCF Ratio", historic_debt_fcf, years)


def get_price_fcf_ratio(ratios, years):
    try:
        price_fcf = ratios.find("span", string="P/FCF Ratio").parent.parent
        year_columns = price_fcf.find_all("td")
    except AttributeError:
        print("There was a problem getting Price/FCF Ratios")
        return

    historic_price_fcf = get_historic_ratio_data_from_rows(year_columns, years)
    display_metrics("Price/FCF Ratio", historic_price_fcf, years)


def get_ttm_fcf(ttm_income_statement):
    try:
        fcf = ttm_income_statement.find("span", string="Free Cash Flow").parent.parent
        ttm_fcf = fcf.find_all("td")[1].text
        return ttm_fcf
    except AttributeError:
        print("There was a problem finding the TTM Free Cash Flow")


def get_ttm_eps(ttm_income_statement):
    try:
        eps = ttm_income_statement.find("span", string="EPS (Diluted)").parent.parent
        ttm_eps = eps.find_all("td")[1].text
        return ttm_eps
    except AttributeError:
        print("There was a problem finding the TTM EPS")


def get_company_name_and_price(income_statement):
    try:
        company_details = income_statement.find_all("div", class_=["text-4xl", "font-bold", "block", "sm:inline"])
        name, price = company_details[0].text, company_details[1].text
        return name, price
    except AttributeError:
        print("There was a problem finding the current price")


def get_market_cap(ratios):
    try:
        market_cap = ratios.find("a", string="Market Capitalization").parent.parent
        current_cap = market_cap.find_all("td")[1].text
        return current_cap
    except AttributeError:
        print("There was a problem finding the current Market Cap")


def discounted_cash_flow_analysis(growth_rate, ttm_fcf, margin_of_safety, terminal_multiplier):
    yearly_fcf_growth = []
    fcf = ttm_fcf
    for i in range(10):
        fcf = fcf * (1 + (growth_rate/100))
        yearly_fcf_growth.append(round(fcf, 2))

    discounted_values = []
    j = 1
    for i in range(10):
        discounted_value = yearly_fcf_growth[i] / 1.15 ** j
        discounted_values.append(round(discounted_value, 2))
        j += 1

    terminal_value = yearly_fcf_growth[9] * terminal_multiplier
    terminal_value_discounted = terminal_value / 1.15 ** 10
    intrinsic_value = round(sum(discounted_values) + terminal_value_discounted, 2)
    intrinsic_value_mos_applied = round(intrinsic_value - (margin_of_safety / 100) * intrinsic_value, 2)
    print(f"Intrinsic Value without MOS Applied: {convert_from_mil_to_bil(intrinsic_value)}B")
    print(f"Intrinsic Value with MOS Applied: {convert_from_mil_to_bil(intrinsic_value_mos_applied)}B")


def get_sticker_price(growth_rate, ttm_eps, margin_of_safety, future_pe):
    future_eps = ttm_eps * (1 + (growth_rate / 100)) ** 10
    future_value = future_eps * future_pe
    current_price = round(future_value / 1.15 ** 10, 2)
    current_price_with_mos = round(current_price - (margin_of_safety / 100) * current_price, 2)
    print(f"Current sticker price without MOS Applied: {current_price}")
    print(f"Current sticker price with MOS Applied: {current_price_with_mos}")


def convert_from_mil_to_bil(value):
    return round(value / 1000, 2)


def main(ticker):
    income_statement = get_income_statement(ticker)
    balance_sheet = get_balance_sheet(ticker)
    ratios = get_ratios_and_metrics(ticker)
    ttm_income_statement = get_ttm_income_statement(ticker)
    income_years_available = get_years_available(income_statement)
    balance_years_available = get_years_available(balance_sheet)
    name, price = get_company_name_and_price(income_statement)
    print(f"Company Name: {name}")
    print(f"Current Price: {price}")
    market_cap = get_market_cap(ratios)
    print(f"Market Cap: {market_cap}M")
    print(f"TTM Free Cash Flow: {get_ttm_fcf(ttm_income_statement)}M")
    print(f"TTM EPS: {get_ttm_eps(ttm_income_statement)}")
    print(f"Analyst Estimated 5 year Growth Rate: {get_analyst_5_year_growth_prediction(ticker)}")
    print("\nEquity Growth Rates")
    get_equity_growth_rates(balance_sheet, balance_years_available)
    print("\nEPS Growth Rates")
    get_eps_growth_rates(income_statement, income_years_available)
    print("\nSales Growth Rates")
    get_sales_growth_rates(income_statement, income_years_available)
    print("\nFree Cash Flow Growth Rates")
    get_free_cash_flow_growth_rates(income_statement, income_years_available)
    print("\nROIC (%)")
    get_roic(ratios, balance_years_available)
    print("\nPE Ratios")
    get_pe_ratio(ratios, balance_years_available)
    print("\nDebt/FCF Ratios")
    get_debt_fcf_ratio(ratios, balance_years_available)
    print("\nPrice/FCF Ratios")
    get_price_fcf_ratio(ratios, balance_years_available)


main("WING")
print("\n")


growth_rate = 17
margin_of_safety = 50

free_cash_flow = 81.09
fcf_multiple = 76

eps = 2.35
future_pe_estimate = 86

discounted_cash_flow_analysis(growth_rate, free_cash_flow, margin_of_safety, fcf_multiple)
print("\n")
get_sticker_price(growth_rate, eps, margin_of_safety, future_pe_estimate)

