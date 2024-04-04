from util import display_metrics, get_years_available, get_soup
import yahoo_fin.stock_info as si


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





def get_market_cap(ratios):
    try:
        market_cap = ratios.find("a", string="Market Capitalization").parent.parent
        current_cap = market_cap.find_all("td")[1].text
        return current_cap
    except AttributeError:
        print("There was a problem finding the current Market Cap")



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


