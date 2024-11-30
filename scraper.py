from bs4 import BeautifulSoup
import requests

from requests import HTTPError


def get_soup(url):
    try:
        headers = {'User-agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        return BeautifulSoup(response.content, "html.parser")
    except HTTPError as hp:
        print(f"Http Error: {hp}")


def get_income_statement(ticker):
    print(f"Getting income statement for {ticker}")
    url = f"https://discountingcashflows.com/company/{ticker}/income-statement/"
    income_statement = get_soup(url)
    return income_statement


def get_ttm_income_statement(ticker):
    print(f"Getting TTM income statement for {ticker}")
    url = f"https://stockanalysis.com/stocks/{ticker}/financials/"
    quarterly_income_statement = get_soup(url)
    return quarterly_income_statement


def get_balance_sheet(ticker):
    print(f"Getting balance sheet for {ticker}")
    url = f"https://discountingcashflows.com/company/{ticker}/balance-sheet-statement/"
    balance_sheet = get_soup(url)
    return balance_sheet


def get_cash_flow_statement(ticker):
    print(f"Getting cash flow statement for {ticker}")
    url = f"https://discountingcashflows.com/company/{ticker}/cash-flow-statement/"
    cash_flow_statement = get_soup(url)
    return cash_flow_statement


def get_ratios(ticker):
    print(f"Getting ratios for {ticker}")
    url = f"https://discountingcashflows.com/company/{ticker}/ratios/"
    ratios = get_soup(url)
    return ratios


def get_analyst_5_year_growth_prediction(ticker):
    print("Getting analyst estimated growth rate")
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}/analysis/"
        soup = get_soup(url)
        growth_section = soup.find("section", {"data-testid": "growthEstimate"})
        next_year_est = growth_section.find("td", string="Next Year").parent.find_all("td")[1].get_text()
        return next_year_est
    except (AttributeError, IndexError):
        return "Not Found"