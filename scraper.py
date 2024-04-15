from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO


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


def get_analyst_5_year_growth_prediction(ticker, headers={'User-agent': 'Mozilla/5.0'}):
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}/analysis"
        tables = pd.read_html(StringIO(requests.get(url, headers=headers).text))
        analyst_5yr_estimate = tables[5][ticker][4]
        return analyst_5yr_estimate
    except AttributeError:
        return "Problem finding analyst growth rate estimate"

