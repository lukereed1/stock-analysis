from bs4 import BeautifulSoup
import requests
import yahoo_fin.stock_info as si


def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, "html.parser")


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


