from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO

from requests import HTTPError


def get_soup(url):
    try:
        response = requests.get(url)
        return BeautifulSoup(response.content, "lxml")
    except HTTPError as hp:
        print(f"Http Error: {hp}")


def get_income_statement(ticker):
    url = f"https://discountingcashflows.com/company/{ticker}/income-statement/"
    income_statement = get_soup(url)
    return income_statement


def get_ttm_income_statement(ticker):
    url = f"https://stockanalysis.com/stocks/{ticker}/financials/"
    quarterly_income_statement = get_soup(url)
    return quarterly_income_statement


def get_balance_sheet(ticker):
    url = f"https://discountingcashflows.com/company/{ticker}/balance-sheet-statement/"
    balance_sheet = get_soup(url)
    return balance_sheet


def get_cash_flow_statement(ticker):
    url = f"https://discountingcashflows.com/company/{ticker}/cash-flow-statement/"
    cash_flow_statement = get_soup(url)
    return cash_flow_statement


def get_ratios(ticker):
    url = f"https://discountingcashflows.com/company/{ticker}/ratios/"
    ratios = get_soup(url)
    return ratios


# def get_analyst_5_year_growth_prediction(ticker, headers={'User-agent': 'Mozilla/5.0'}):
#     try:
#         url = f"https://finance.yahoo.com/quote/{ticker}/analysis"
#         tables = pd.read_html(StringIO(requests.get(url, headers=headers).text))
#         analyst_5yr_estimate = tables[5][ticker][4]
#         return analyst_5yr_estimate
#     except (AttributeError, IndexError):
#         return "Not Found"
#
