import tkinter as tk
from tkinter import messagebox
from calcs import dcfa_calc, get_sticker_price, calculate_growth_rate, add_commas_to_num
from scraper import (get_income_statement, get_ttm_income_statement, get_balance_sheet,
                     get_ratios_and_metrics, get_analyst_5_year_growth_prediction)
from data_processing import (get_market_cap, get_years_available, get_company_name_and_price, get_ttm_fcf, get_ttm_eps,
                             get_sales_growth_rates, get_eps_growth_rates, get_free_cash_flow_growth_rates,
                             get_equity_growth_rates, get_roic, get_pe_ratio, get_price_fcf_ratio,
                             get_debt_equity_ratio)

import matplotlib.pyplot as plt


def main(ticker):
    income_statement = get_income_statement(ticker)
    balance_sheet = get_balance_sheet(ticker)
    ratios_and_metrics = get_ratios_and_metrics(ticker)
    # ttm_income_statement = get_ttm_income_statement(ticker)
    income_years_available, income_year_list = get_years_available(income_statement)
    balance_years_available, balance_year_list = get_years_available(balance_sheet)
    print(income_year_list)
    print(balance_year_list)
    roic_averages, all_roic = get_roic(ratios_and_metrics, balance_years_available)
    pe_averages, all_pe = get_pe_ratio(ratios_and_metrics, balance_years_available)
    print(roic_averages)
    print(all_roic)
    h = {}
    v = {}
    for i in range(balance_years_available):
        h[balance_year_list[i]] = all_roic[i+1]

    for i in range(balance_years_available):
        v[balance_year_list[i]] = all_pe[i+1]
    graph(h, "Test graph", "Years", "ROIC (%)")


def graph(data_dict, title, x_title, y_title):
    x = list(data_dict.keys())[::-1]
    y = list(data_dict.values())[::-1]

    fig = plt.figure(figsize=(8, 5))
    plt.bar(x, y, color="blue", width=0.7)
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(title)
    plt.text(1, 10, "hi", ha="center")
    plt.show()



main("AAPL")
