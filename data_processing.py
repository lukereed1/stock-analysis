from calcs import calculate_growth_rate


def get_sales_growth_rates(income_statement, years):
    try:
        gross_profits = income_statement.find("span", string="Gross Profit").parent.parent
        year_columns = gross_profits.find_all("td")
    except AttributeError:
        print("There was a problem finding Gross Profits")
        return

    historic_profits = get_historic_growth_data_from_rows(year_columns, years)
    return find_growth_rates(historic_profits, years)


def get_eps_growth_rates(income_statement, years):
    try:
        eps = income_statement.find("span", string="EPS (Diluted)").parent.parent
        year_columns = eps.find_all("td")
    except AttributeError:
        print("There was a problem finding EPS")
        return

    historic_eps = get_historic_growth_data_from_rows(year_columns, years)
    return find_growth_rates(historic_eps, years)


def get_free_cash_flow_growth_rates(income_statement, years):
    try:
        fcf = income_statement.find("span", string="Free Cash Flow").parent.parent
        year_columns = fcf.find_all("td")
    except AttributeError:
        print("There was a problem finding Free Cash Flow")
        return

    historic_fcf = get_historic_growth_data_from_rows(year_columns, years)
    return find_growth_rates(historic_fcf, years)


def get_equity_growth_rates(balance_sheet, years):
    try:
        equity = balance_sheet.find("span", string="Shareholders' Equity").parent.parent
        year_columns = equity.find_all("td")
    except AttributeError:
        print("There was a problem finding Equity values")
        return

    historic_equity = get_historic_growth_data_from_rows(year_columns, years)
    return find_growth_rates(historic_equity, years)


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
        roic = ratios.find("span", string="Return on Capital (ROIC)").parent.parent
        year_columns = roic.find_all("td")
    except AttributeError:
        print("There was a problem finding this ratio")
        return

    historic_roic = get_historic_ratio_data_from_rows(year_columns, years)
    return find_ratio_averages(historic_roic, years)


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
        pe = ratios.find("span", string="PE Ratio").parent.parent
        year_columns = pe.find_all("td")
    except AttributeError:
        print("There was a problem finding PE Ratios")
        return

    historic_pe = get_historic_ratio_data_from_rows(year_columns, years)
    return find_ratio_averages(historic_pe, years)


def get_debt_fcf_ratio(ratios, years):
    try:
        debt_fcf = ratios.find("span", string="Debt / FCF Ratio").parent.parent
        year_columns = debt_fcf.find_all("td")
    except AttributeError:
        print("There was a problem getting Debt/FCF Ratios")
        return

    historic_debt_fcf = get_historic_ratio_data_from_rows(year_columns, years)
    return find_ratio_averages(historic_debt_fcf, years)


def get_price_fcf_ratio(ratios, years):
    try:
        price_fcf = ratios.find("span", string="P/FCF Ratio").parent.parent
        year_columns = price_fcf.find_all("td")
    except AttributeError:
        print("There was a problem getting Price/FCF Ratios")
        return

    historic_price_fcf = get_historic_ratio_data_from_rows(year_columns, years)
    return find_ratio_averages(historic_price_fcf, years)


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


def get_market_cap(ratios):
    try:
        market_cap = ratios.find("a", string="Market Capitalization").parent.parent
        current_cap = market_cap.find_all("td")[1].text
        return current_cap
    except AttributeError:
        print("There was a problem finding the current Market Cap")


def get_years_available(soup):
    years = len(soup.find_all("th", {"class": "border-b"}))
    #  Removes columns that don't reflect a certain year
    if years > 11:
        years -= 2
    else:
        years -= 1
    return years


def get_company_name_and_price(income_statement):
    try:
        company_details = income_statement.find_all("div", class_=["text-4xl", "font-bold", "block", "sm:inline"])
        name, price = company_details[0].text, company_details[1].text
        return name, price
    except IndexError:
        print("There was a problem finding the current price")
        return "N/A", "N/A"





