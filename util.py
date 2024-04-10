from bs4 import BeautifulSoup
import requests


def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, "html.parser")


def convert_from_mil_to_bil(value):
    return round(value / 1000, 2)




