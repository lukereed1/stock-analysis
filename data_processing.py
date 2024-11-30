from calcs import calculate_growth_rate
from scraper import get_income_statement, get_cash_flow_statement, get_ttm_income_statement, get_balance_sheet, \
    get_ratios


def get_sales_growth_rates(income_statement, years):
    try:
        gross_profits = income_statement.find("span", string="Gross Profit").parent.parent.parent
        values = gross_profits.find_all("td", class_="formatted-value")
        data = []
        for i in range(years):
            amount = values[i].get_text().replace(",", "")
            data.append(float(amount))
        return find_growth_rates(data, years), data
    except AttributeError:
        print("There was a problem finding Gross Profits")
        return

    # historic_profits = get_historic_growth_data_from_rows(year_columns, years)
    # return find_growth_rates(historic_profits, years), historic_profits


def get_eps_growth_rates(income_statement, years):
    try:
        eps = income_statement.find("span", string="Earnings Per Share (EPS)").parent.parent.parent
        values = eps.find_all("td", class_="formatted-value")
        data = []
        for i in range(years):
            amount = values[i].get_text().replace(",", "")
            data.append(float(amount))
        return find_growth_rates(data, years), data
    except AttributeError:
        print("There was a problem finding EPS")
        return

    # historic_eps = get_historic_growth_data_from_rows(year_columns, years)
    # return find_growth_rates(historic_eps, years), historic_eps


def get_free_cash_flow_growth_rates(cash_flow_statement, years):
    try:
        fcf = cash_flow_statement.find("span", string="Free Cash Flow").parent.parent.parent
        values = fcf.find_all("td", class_="formatted-value")
        data = []
        for i in range(years):
            amount = values[i].get_text().replace(",", "")
            data.append(float(amount))
        return find_growth_rates(data, years), data
    except AttributeError:
        print("There was a problem finding Free Cash Flow")
        return

    # historic_fcf = get_historic_growth_data_from_rows(year_columns, years)
    # return find_growth_rates(historic_fcf, years), historic_fcf


def get_equity_growth_rates(balance_sheet, years):
    try:
        equity = balance_sheet.find("span", string="Total Stockholders' Equity").parent.parent.parent
        values = equity.find_all("td", class_="formatted-value")
        data = []
        for i in range(years):
            amount = values[i].get_text().replace(",", "")
            data.append(float(amount))
        return find_growth_rates(data, years), data

    except AttributeError:
        print("There was a problem finding Equity values")
        return

    # historic_equity = get_historic_growth_data_from_rows(year_columns, years)
    # return find_growth_rates(historic_equity, years), historic_equity


def find_growth_rates(historic_data, years):
    latest = historic_data[0]
    initial_amount = historic_data[len(historic_data) - 1]
    ten_year_growth_rate, five_year_growth_rate = 0, 0
    if years == 10:
        ten_year_growth_rate = calculate_growth_rate(10, initial_amount, latest)
    else:
        ten_year_growth_rate = calculate_growth_rate(years, initial_amount, latest)

    if years >= 5:
        five_year_growth_rate = calculate_growth_rate(5, historic_data[4], latest)

    one_year_growth_rate = calculate_growth_rate(2, historic_data[1], latest)

    return one_year_growth_rate, five_year_growth_rate, ten_year_growth_rate


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


def get_roic(ratios, years):
    try:
        roic = ratios.find("td", class_="ltm-returnOnInvestedCapital").parent
        values = roic.find_all("td")
        values = values[2:]
        data = []
        for i in range(years):
            amount = values[i].get_text().strip().replace("%", "")
            data.append(float(amount))
        return find_ratio_averages(data, years), data
    except AttributeError:
        print("There was a problem finding this ratio")
        return

    # historic_roic = get_historic_ratio_data_from_rows(year_columns, years)
    # return find_ratio_averages(historic_roic, years), historic_roic


def find_ratio_averages(historic_data, years):
    if historic_data is None:
        return
    ten_year_average, five_year_average = round(sum(historic_data[1:]) / years, 2), 0

    if years >= 5:
        five_year_average = round(sum(historic_data[1:6]) / 5, 2)

    ttm = historic_data[0]

    return ttm, five_year_average, ten_year_average


def get_pe_ratio(ratios, years):
    try:
        pe = ratios.find("td", class_="ltm-priceEarningsRatio").parent
        values = pe.find_all("td")
        values = values[2:]
        data = []
        for i in range(years):
            amount = values[i].get_text().strip()
            data.append(float(amount))
        return find_ratio_averages(data, years), data
    except AttributeError:
        print("There was a problem finding PE Ratios")
        return

    # historic_pe = get_historic_ratio_data_from_rows(year_columns, years)
    # return find_ratio_averages(historic_pe, years), historic_pe


def get_debt_equity_ratio(ratios, years):
    try:
        de = ratios.find("td", class_="ltm-debtEquityRatio").parent
        values = de.find_all("td")
        values = values[2:]
        data = []
        for i in range(years):
            amount = values[i].get_text().strip()
            data.append(float(amount))
        return find_ratio_averages(data, years), data
    except AttributeError:
        print("There was a problem getting Debt/FCF Ratios")
        return

    # historic_debt_equity = get_historic_ratio_data_from_rows(year_columns, years)
    # return find_ratio_averages(historic_debt_equity, years), historic_debt_equity


def get_price_fcf_ratio(ratios, years):
    try:
        p_fcf = ratios.find("td", class_="ltm-priceToFreeCashFlowsRatio").parent
        values = p_fcf.find_all("td")
        values = values[2:]
        data = []
        for i in range(years):
            amount = values[i].get_text().strip()
            data.append(float(amount))
        return find_ratio_averages(data, years), data
    except AttributeError:
        print("There was a problem getting Price/FCF Ratios")
        return

    # historic_price_fcf = get_historic_ratio_data_from_rows(year_columns, years)
    # return find_ratio_averages(historic_price_fcf, years), historic_price_fcf


def get_ttm_fcf(income_statement):
    try:
        fcf = income_statement.find("div", string="Free Cash Flow").parent.parent.parent.find_all("td")[1]
        return fcf.get_text()
    except AttributeError:
        print("There was a problem finding the TTM Free Cash Flow")


def get_ttm_eps(income_statement):
    try:
        eps = income_statement.find("div", string="EPS (Diluted)").parent.parent.parent.find_all("td")[1]
        return eps.get_text()
    except AttributeError:
        print("There was a problem finding the TTM EPS")


def get_market_cap(ttm_income_statement, price):
    try:
        shares = ttm_income_statement.find("div", string="Shares Outstanding (Basic)").parent.parent.parent.find_all("td")[1].get_text().replace(",", "")
        return float(shares) * float(price)
    except AttributeError:
        print("There was a problem finding the current Market Cap")


def get_years_available(soup):
    data_columns = len(soup.find_all("th", class_="py-0 px-3 text-center")) - 1

    if data_columns > 10:
        data_columns = 10

    years = soup.find_all("th", class_="py-0 px-3 text-center")
    available_years = []
    for i in range(1, data_columns + 1):
        year_text = years[i].find("span", class_="text-nowrap").get_text()
        available_years.append(year_text)

    return data_columns, available_years


def get_balance_years_available(soup):
    data_columns = len(soup.find_all("th", class_="py-0 px-3 text-center"))

    if data_columns > 10:
        data_columns = 10

    years = soup.find_all("th", class_="py-0 px-3 text-center")
    available_years = []
    for i in range(data_columns):
        year_text = years[i].find("span", class_="text-nowrap").get_text()
        available_years.append(year_text)

    return data_columns, available_years


def get_company_name_and_price(income_statement):
    try:
        company_details = income_statement.find("div", class_="mx-auto mb-2")
        name = company_details.find("div", class_="mb-0 text-2xl font-bold text-default sm:text-[26px]").get_text()
        price = company_details.find("div", class_="text-4xl").get_text()
        return name, price
    except IndexError:
        print("There was a problem finding the current price")
        return "N/A", "N/A"


income = get_ttm_income_statement("YETI")
get_company_name_and_price(income)