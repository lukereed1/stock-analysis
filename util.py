from bs4 import BeautifulSoup
import requests


def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, "html.parser")


def convert_from_mil_to_bil(value):
    return round(value / 1000, 2)


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

