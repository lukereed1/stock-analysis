from growth_rates import (get_income_statement,get_balance_sheet, get_ttm_income_statement, get_equity_growth_rates,
                          get_sales_growth_rates, get_eps_growth_rates, get_free_cash_flow_growth_rates)
from metrics import (get_ratios_and_metrics, get_analyst_5_year_growth_prediction, get_market_cap, get_ttm_fcf,
                     get_ttm_eps, get_debt_fcf_ratio, get_price_fcf_ratio, get_roic, get_pe_ratio)
from util import get_years_available, get_company_name_and_price
from calcs import discounted_cash_flow_analysis, get_sticker_price


def main(ticker):
    income_statement = get_income_statement(ticker)
    balance_sheet = get_balance_sheet(ticker)
    ratios = get_ratios_and_metrics(ticker)
    ttm_income_statement = get_ttm_income_statement(ticker)
    income_years_available = get_years_available(income_statement)
    balance_years_available = get_years_available(balance_sheet)
    name, price = get_company_name_and_price(income_statement)
    print(f"Company Name: {name}")
    print(f"Current Price: {price}")
    market_cap = get_market_cap(ratios)
    print(f"Market Cap: {market_cap}M")
    print(f"TTM Free Cash Flow: {get_ttm_fcf(ttm_income_statement)}M")
    print(f"TTM EPS: {get_ttm_eps(ttm_income_statement)}")
    print(f"Analyst Estimated 5 year Growth Rate: {get_analyst_5_year_growth_prediction(ticker)}")
    print("\nEquity Growth Rates")
    get_equity_growth_rates(balance_sheet, balance_years_available)
    print("\nEPS Growth Rates")
    get_eps_growth_rates(income_statement, income_years_available)
    print("\nSales Growth Rates")
    get_sales_growth_rates(income_statement, income_years_available)
    print("\nFree Cash Flow Growth Rates")
    get_free_cash_flow_growth_rates(income_statement, income_years_available)
    print("\nROIC (%)")
    get_roic(ratios, balance_years_available)
    print("\nPE Ratios")
    get_pe_ratio(ratios, balance_years_available)
    print("\nDebt/FCF Ratios")
    get_debt_fcf_ratio(ratios, balance_years_available)
    print("\nPrice/FCF Ratios")
    get_price_fcf_ratio(ratios, balance_years_available)


main("LULU")
print("\n")

growth_rate = 12.3
margin_of_safety = 30

free_cash_flow = 1644
fcf_multiple = 40

eps = 12.2
future_pe_estimate = 25

discounted_cash_flow_analysis(growth_rate, free_cash_flow, margin_of_safety, fcf_multiple)
print("\n")
get_sticker_price(growth_rate, eps, margin_of_safety, future_pe_estimate)
