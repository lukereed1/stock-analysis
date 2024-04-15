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


class GUI:
    def __init__(self, root):
        self.root = root
        root.title("Stock Analysis")
        root.geometry("1000x650")
        self.create_widgets()

    def handle_search(self):
        search_value = getattr(self, "search_bar").get().upper()
        if not search_value.strip():
            self.popup_message("Enter a valid ticker")
            return
        try:
            self.get_stock_info(search_value)
        except (ValueError, KeyError):
            self.popup_message("There was a problem finding this stock")
            return

        self.fill_calculators()

    def handle_equity_graph_button(self):
        equity_map = self.create_data_map("historic_equity", "income")
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"Equity Chart for {company_name}",
            "Year",
            "Equity (Millions)",
            equity_map
        )

    def handle_eps_graph_button(self):
        eps_map = self.create_data_map("historic_eps", "income")
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"EPS Chart for {company_name}",
            "Year",
            "EPS",
            eps_map
        )

    def handle_sales_button(self):
        sales_map = self.create_data_map("historic_sales", "income")
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"Sales Chart for {company_name}",
            "Year",
            "Sales (Millions)",
            sales_map
        )

    def handle_fcf_graph_button(self):
        fcf_map = self.create_data_map("historic_cash", "income")
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"Free Cash Flow Chart for {company_name}",
            "Year",
            "FCF (Millions)",
            fcf_map
        )

    def handle_roic_graph_button(self):
        roic_map = self.create_data_map("historic_roic", "balance")
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"ROIC (%) Chart for {company_name}",
            "Year",
            "ROIC (%)",
            roic_map
        )

    def handle_pe_graph_button(self):
        pe_map = self.create_data_map("historic_pe", "balance")
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"PE Ratio Chart for {company_name}",
            "Year",
            "PE Ratio",
            pe_map
        )

    def handle_p_fcf_graph_buttonm(self):
        p_fcf_map = self.create_data_map("historic_p_fcf", "balance")
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"P/FCF Ratio Chart for {company_name}",
            "Year",
            "Price/FCF Ratio",
            p_fcf_map
        )

    def handle_debt_equity_graph_button(self):
        debt_equity_map = self.create_data_map("historic_debt_equity", "balance")
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"Debt/Equity Ratio Chart for {company_name}",
            "Year",
            "Debt/Equity Ratio",
            debt_equity_map
        )

    def create_data_map(self, metric, statement):
        data_map = {}
        historic_data = getattr(self, metric)
        if statement == "balance":
            year_list = getattr(self, "balance_year_list")
            for i in range(len(year_list)):
                data_map[year_list[i]] = historic_data[i + 1]
        else:
            year_list = getattr(self, "income_year_list")
            for i in range(len(year_list)):
                data_map[year_list[i]] = historic_data[i]

        return data_map

    def show_chart(self, title, x_title, y_title, data_map):
        x_data = list(data_map.keys())[::-1]
        y_data = list(data_map.values())[::-1]
        fig = plt.figure(figsize=(8, 5))
        plt.bar(x_data, y_data, color="blue", width=0.7)
        plt.xlabel(x_title)
        plt.ylabel(y_title)
        plt.title(title)
        plt.show()

    @staticmethod
    def popup_message(message):
        messagebox.showinfo("Error", message)

    def fill_calculators(self):
        analsyt_est_growth = getattr(self, "est_growth_data").get()
        analsyt_est_growth = analsyt_est_growth.replace("%", "")
        ttm_fcf = getattr(self, "fcf_data").get()
        ttm_fcf = ttm_fcf.replace(",", "")
        p_fcf_avg = getattr(self, "ten_year_p_fcf").get()
        ttm_eps = getattr(self, "eps_data").get()
        pe_avg = getattr(self, "ten_year_pe").get()
        self.set_data("dcfa_growth_rate", analsyt_est_growth)
        self.set_data("dcfa_ttm_fcf", ttm_fcf)
        self.set_data("dcfa_p_fcf", p_fcf_avg)
        self.set_data("dcfa_mos", 50)
        self.set_data("sticker_eps", ttm_eps)
        self.set_data("sticker_growth_rate", analsyt_est_growth)
        self.set_data("sticker_future_pe", pe_avg)
        self.set_data("sticker_calc_mos", 50)
        self.set_data("intrin_no_mos", "")
        self.set_data("intrin_with_mos", "")
        self.set_data("sticker_no_mos", "")
        self.set_data("sticker_with_mos", "")

    def get_stock_info(self, ticker):
        income_statement = get_income_statement(ticker)
        balance_sheet = get_balance_sheet(ticker)
        ratios_and_metrics = get_ratios_and_metrics(ticker)
        ttm_income_statement = get_ttm_income_statement(ticker)
        income_years_available, income_year_list = get_years_available(income_statement)
        balance_years_available, balance_year_list = get_years_available(balance_sheet)
        analyst_estimated_growth = get_analyst_5_year_growth_prediction(ticker)
        setattr(self, "income_year_list", income_year_list)
        setattr(self, "balance_year_list", balance_year_list)
        self.set_summary(income_statement, ttm_income_statement, ratios_and_metrics, analyst_estimated_growth)
        self.set_growth(income_statement, balance_sheet, income_years_available, balance_years_available)
        self.set_ratios(ratios_and_metrics, balance_years_available)

    def set_summary(self, income_statement, ttm_income_statement, ratios_and_metrics, analyst_growth_est):
        name, price = get_company_name_and_price(income_statement)
        market_cap = get_market_cap(ratios_and_metrics)
        ttm_fcf = get_ttm_fcf(ttm_income_statement)
        ttm_eps = get_ttm_eps(ttm_income_statement)
        self.set_data("name_data", name)
        self.set_data("est_growth_data", analyst_growth_est)
        self.set_data("cap_data", market_cap)
        self.set_data("price_data", price)
        self.set_data("fcf_data", ttm_fcf)
        self.set_data("eps_data", ttm_eps)

    def set_growth(self, income_statement, balance_sheet, income_years_available, balance_years_available):
        equity_averages, all_equity = get_equity_growth_rates(balance_sheet, balance_years_available)
        setattr(self, "historic_equity", all_equity)
        self.set_data("one_year_equity", equity_averages[0])
        self.set_data("five_year_equity", equity_averages[1])
        self.set_data("ten_year_equity", equity_averages[2])

        eps_averages, all_eps = get_eps_growth_rates(income_statement, income_years_available)
        setattr(self, "historic_eps", all_eps)
        self.set_data("one_year_eps", eps_averages[0])
        self.set_data("five_year_eps", eps_averages[1])
        self.set_data("ten_year_eps", eps_averages[2])

        sales_averages, all_sales = get_sales_growth_rates(income_statement, income_years_available)
        setattr(self, "historic_sales", all_sales)
        self.set_data("one_year_sales", sales_averages[0])
        self.set_data("five_year_sales", sales_averages[1])
        self.set_data("ten_year_sales", sales_averages[2])

        cash_averages, all_cash = get_free_cash_flow_growth_rates(income_statement, income_years_available)
        setattr(self, "historic_cash", all_cash)
        self.set_data("one_year_cash", cash_averages[0])
        self.set_data("five_year_cash", cash_averages[1])
        self.set_data("ten_year_cash", cash_averages[2])

    def set_ratios(self, ratios_and_metrics, years_available):
        roic_averages, all_roic = get_roic(ratios_and_metrics, years_available)
        setattr(self, "historic_roic", all_roic)
        self.set_data("ttm_roic", roic_averages[0])
        self.set_data("five_year_roic", roic_averages[1])
        self.set_data("ten_year_roic", roic_averages[2])

        pe_averages, all_pe = get_pe_ratio(ratios_and_metrics, years_available)
        setattr(self, "historic_pe", all_pe)
        self.set_data("ttm_pe", pe_averages[0])
        self.set_data("five_year_pe", pe_averages[1])
        self.set_data("ten_year_pe", pe_averages[2])

        p_fcf_averages, all_p_fcf = get_price_fcf_ratio(ratios_and_metrics, years_available)
        setattr(self, "historic_p_fcf", all_p_fcf)
        self.set_data("ttm_p_fcf", p_fcf_averages[0])
        self.set_data("five_year_p_fcf", p_fcf_averages[1])
        self.set_data("ten_year_p_fcf", p_fcf_averages[2])

        debt_equity_averages, all_debt_equity = get_debt_equity_ratio(ratios_and_metrics, years_available)
        setattr(self, "historic_debt_equity", all_debt_equity)
        self.set_data("ttm_d_fcf", debt_equity_averages[0])
        self.set_data("five_year_d_fcf", debt_equity_averages[1])
        self.set_data("ten_year_d_fcf", debt_equity_averages[2])

    def calculate_growth_rate(self):
        start_amount = getattr(self, "start_amount").get()
        end_amount = getattr(self, "end_amount").get()
        years = getattr(self, "years").get()
        try:
            start_amount = float(start_amount)
            end_amount = float(end_amount)
            years = float(years)
        except ValueError:
            self.popup_message("All values must be a positive number")
            return

        growth_rate = calculate_growth_rate(years, start_amount, end_amount)
        self.set_data("calc_growth_rate", growth_rate)

    def calculate_dcfa(self):
        ttm_fcf = getattr(self, "dcfa_ttm_fcf").get()
        growth_rate = getattr(self, "dcfa_growth_rate").get()
        p_fcf_value = getattr(self, "dcfa_p_fcf").get()
        margin_of_safety = getattr(self, "dcfa_mos").get()

        try:
            ttm_fcf = float(ttm_fcf)
            growth_rate = float(growth_rate)
            p_fcf_value = float(p_fcf_value)
            margin_of_safety = float(margin_of_safety)
        except ValueError:
            self.popup_message("Ensure all inputs are valid")
            return

        intrinsic_value, intrinsic_value_with_mos = dcfa_calc(growth_rate, ttm_fcf, margin_of_safety, p_fcf_value)
        self.set_data("intrin_no_mos", add_commas_to_num(intrinsic_value))
        self.set_data("intrin_with_mos", add_commas_to_num(intrinsic_value_with_mos))

    def calculate_sticker_price(self):
        ttm_eps = getattr(self, "sticker_eps").get()
        growth_rate = getattr(self, "sticker_growth_rate").get()
        future_pe = getattr(self, "sticker_future_pe").get()
        margin_of_safety = getattr(self, "sticker_calc_mos").get()

        try:
            ttm_eps = float(ttm_eps)
            growth_rate = float(growth_rate)
            future_pe = float(future_pe)
            margin_of_safety = float(margin_of_safety)
        except ValueError:
            self.popup_message("Ensure all inputs are valid")
            return

        current_price, current_price_with_mos = get_sticker_price(growth_rate, ttm_eps, margin_of_safety, future_pe)
        self.set_data("sticker_no_mos", current_price)
        self.set_data("sticker_with_mos", current_price_with_mos)

    def set_data(self, entry_name, data):
        entry = getattr(self, entry_name)
        entry.delete(0, tk.END)
        entry.insert(0, data)

    def create_widgets(self):
        self.search_bar_section()
        self.business_summary_section()
        self.historic_data()
        self.calculations_section()

    def search_bar_section(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=20)

        search_label = tk.Label(search_frame, text="Enter Stock Ticker:")
        search_label.grid(row=0, column=0, padx=5)

        search_entry = tk.Entry(search_frame)
        setattr(self, "search_bar", search_entry)
        search_entry.grid(row=0, column=1, padx=5)

        search_button = tk.Button(search_frame, text="Search", command=self.handle_search)
        search_button.grid(row=0, column=2, padx=5)

    def business_summary_section(self):
        summary_frame = tk.Frame(self.root)
        summary_frame.pack(pady=10)
        labels = ["Business Name", "Analyst Est. Growth", "Market Cap", "Current Price", "TTM FCF", "TTM EPS"]
        entries = ["name_data", "est_growth_data", "cap_data", "price_data", "fcf_data", "eps_data"]

        col = 0
        for i in range(len(labels)):
            data_label = tk.Label(summary_frame, text=labels[i])
            if i == 2 or i == 3:
                data_label.grid(row=i % 2, column=col, padx=(40, 0))
            else:
                data_label.grid(row=i % 2, column=col)

            data_entry = tk.Entry(summary_frame, width=15)
            setattr(self, entries[i], data_entry)
            if i == 2 or i == 3:
                data_entry.grid(row=i % 2, column=col + 1, padx=(0, 40))
            else:
                data_entry.grid(row=i % 2, column=col + 1)

            if i % 2 == 1:
                col += 2

    def historic_data(self):
        historic_data_frame = tk.Frame(self.root)
        historic_data_frame.pack(pady=20)
        self.growth_data(historic_data_frame)
        self.ratios_data(historic_data_frame)

    def growth_data(self, historic_data_frame):
        growth_rates_frame = tk.Frame(historic_data_frame)
        growth_rates_frame.pack(padx=(0, 25), side=tk.LEFT)
        growth_labels = ["Equity Growth", "EPS Growth", "Sales Growth", "FCF Growth"]
        time_labels = ["1 Year", "5 Year", "10 Year"]

        for i in range(len(time_labels)):
            label = tk.Label(growth_rates_frame, text=time_labels[i])
            if i == 1:
                label.grid(row=0, column=i + 1, pady=(0, 10), padx=10)
            else:
                label.grid(row=0, column=i + 1, pady=(0, 10))

        for i in range(len(growth_labels)):
            label = tk.Label(growth_rates_frame, text=growth_labels[i])
            label.grid(row=i + 1, column=0, padx=(0, 10))

        self.growth_data_entries(growth_rates_frame)
        self.graph_button(1, 4, growth_rates_frame, self.handle_equity_graph_button)
        self.graph_button(2, 4, growth_rates_frame, self.handle_eps_graph_button)
        self.graph_button(3, 4, growth_rates_frame, self.handle_sales_button)
        self.graph_button(4, 4, growth_rates_frame, self.handle_fcf_graph_button)

    def graph_button(self, row, col, frame, command):
        button = tk.Button(frame, text=">", command=command)
        button.grid(row=row, column=col)

    def growth_data_entries(self, growth_rates_frame):
        equity_labels = ["one_year_equity", "five_year_equity", "ten_year_equity"]
        eps_labels = ["one_year_eps", "five_year_eps", "ten_year_eps"]
        sales_labels = ["one_year_sales", "five_year_sales", "ten_year_sales"]
        cash_labels = ["one_year_cash", "five_year_cash", "ten_year_cash"]

        for i in range(3):
            equity_entry = tk.Entry(growth_rates_frame, width=7)
            equity_entry.grid(row=1, column=i + 1)
            setattr(self, equity_labels[i], equity_entry)

            eps_entry = tk.Entry(growth_rates_frame, width=7)
            eps_entry.grid(row=2, column=i + 1)
            setattr(self, eps_labels[i], eps_entry)

            sales_entry = tk.Entry(growth_rates_frame, width=7)
            sales_entry.grid(row=3, column=i + 1)
            setattr(self, sales_labels[i], sales_entry)

            cash_entry = tk.Entry(growth_rates_frame, width=7)
            cash_entry.grid(row=4, column=i + 1)
            setattr(self, cash_labels[i], cash_entry)

    def ratios_data(self, historic_data_frame):
        ratios_frame = tk.Frame(historic_data_frame)
        ratios_frame.pack(padx=(25, 0), side=tk.RIGHT)
        ratio_labels = ["ROIC (%)", "PE Ratio", "P/FCF Ratio", "Debt/Equity Ratio"]
        time_labels = ["TTM", "5 Year", "10 Year"]

        for i in range(len(time_labels)):
            label = tk.Label(ratios_frame, text=time_labels[i])
            if i == 1:
                label.grid(row=0, column=i + 1, pady=(0, 10), padx=10)
            else:
                label.grid(row=0, column=i + 1, pady=(0, 10))

        for i in range(len(ratio_labels)):
            label = tk.Label(ratios_frame, text=ratio_labels[i])
            label.grid(row=i + 1, column=0, padx=(0, 10))

        self.ratios_data_entries(ratios_frame)
        self.graph_button(1, 4, ratios_frame, self.handle_roic_graph_button)
        self.graph_button(2, 4, ratios_frame, self.handle_pe_graph_button)
        self.graph_button(3, 4, ratios_frame, self.handle_p_fcf_graph_buttonm)
        self.graph_button(4, 4, ratios_frame, self.handle_debt_equity_graph_button)


    def ratios_data_entries(self, ratio_frame):
        roic_labels = ["ttm_roic", "five_year_roic", "ten_year_roic"]
        pe_labels = ["ttm_pe", "five_year_pe", "ten_year_pe"]
        price_fcf_labels = ["ttm_p_fcf", "five_year_p_fcf", "ten_year_p_fcf"]
        debt_fcf_labels = ["ttm_d_fcf", "five_year_d_fcf", "ten_year_d_fcf"]

        for i in range(3):
            roic_entry = tk.Entry(ratio_frame, width=7)
            roic_entry.grid(row=1, column=i + 1)
            setattr(self, roic_labels[i], roic_entry)

            pe_entry = tk.Entry(ratio_frame, width=7)
            pe_entry.grid(row=2, column=i + 1)
            setattr(self, pe_labels[i], pe_entry)

            p_fcf_entry = tk.Entry(ratio_frame, width=7)
            p_fcf_entry.grid(row=3, column=i + 1)
            setattr(self, price_fcf_labels[i], p_fcf_entry)

            d_fcf_entry = tk.Entry(ratio_frame, width=7)
            d_fcf_entry.grid(row=4, column=i + 1)
            setattr(self, debt_fcf_labels[i], d_fcf_entry)

    def calculations_section(self):
        calc_frame = tk.Frame(self.root)
        calc_frame.pack(pady=20)
        self.growth_calc_section(calc_frame)
        self.dcfa_calc_section(calc_frame)
        self.sticker_price_calc_section(calc_frame)

    def growth_calc_section(self, calc_frame):
        growth_calc_frame = tk.Frame(calc_frame)
        growth_calc_frame.grid(row=0, column=0, padx=(0, 25))
        growth_rate_calc_label = tk.Label(growth_calc_frame, text="Growth Rate Calculator")
        growth_rate_calc_label.grid(row=0, columnspan=2, sticky="EW", pady=(0, 10))
        growth_rate_calc_label.config(font=("TkDefaultFont", 16, "bold"))

        growth_calc_labels = ["Start Amount", "End Amount", "Years", "Annual Growth Rate (%)"]
        growth_calc_entries = ["start_amount", "end_amount", "years", "calc_growth_rate"]
        for i in range(4):
            label = tk.Label(growth_calc_frame, text=growth_calc_labels[i])
            entry = tk.Entry(growth_calc_frame, width=7)
            setattr(self, growth_calc_entries[i], entry)
            if i == 3:
                label.grid(row=i + 2, column=0)
                entry.grid(row=i + 2, column=1)
            else:
                label.grid(row=i + 1, column=0)
                entry.grid(row=i + 1, column=1)

        growth_calc_button = tk.Button(growth_calc_frame, text="Calculate", command=self.calculate_growth_rate)
        growth_calc_button.grid(row=4, columnspan=2, sticky="EW", pady=10)

    def dcfa_calc_section(self, calc_frame):
        dcfa_calc_frame = tk.Frame(calc_frame)
        dcfa_calc_frame.grid(row=0, column=1, padx=50)
        dcfa_calc_label = tk.Label(dcfa_calc_frame, text="Discounted Cash Flow Analysis")
        dcfa_calc_label.grid(row=0, columnspan=2, sticky="EW", pady=(0, 10))
        dcfa_calc_label.config(font=("tkDefaultFont", 16, "bold"))

        dcfa_labels = ["TTM FCF", "Growth Rate (%)", "P/FCF Average",
                       "Margin of Safety (%)", "Intrinsic Value no MOS", "Intrinsic Value with MOS"]
        dcfa_entries = ["dcfa_ttm_fcf", "dcfa_growth_rate", "dcfa_p_fcf",
                        "dcfa_mos", "intrin_no_mos", "intrin_with_mos"]

        for i in range(4):
            label = tk.Label(dcfa_calc_frame, text=dcfa_labels[i])
            label.grid(row=i + 1, column=0)

            entry = tk.Entry(dcfa_calc_frame, width=7)
            setattr(self, dcfa_entries[i], entry)
            entry.grid(row=i + 1, column=1)

        dcfa_calc_button = tk.Button(dcfa_calc_frame, text="Calculate", command=self.calculate_dcfa)
        dcfa_calc_button.grid(columnspan=2, sticky="EW", pady=10)

        for i in range(4, 6):
            label = tk.Label(dcfa_calc_frame, text=dcfa_labels[i])
            label.grid(row=i + 2, column=0)

            entry = tk.Entry(dcfa_calc_frame, width=12)
            setattr(self, dcfa_entries[i], entry)
            entry.grid(row=i + 2, column=1)

    def sticker_price_calc_section(self, calc_frame):
        sticker_calc_frame = tk.Frame(calc_frame)
        sticker_calc_frame.grid(row=0, column=2, padx=(25, 0))
        sticker_price_calc_label = tk.Label(sticker_calc_frame, text="Sticker Price Calculation")
        sticker_price_calc_label.grid(row=0, columnspan=2, sticky="EW", pady=(0, 10), padx=(20, 0))
        sticker_price_calc_label.config(font=("tkDefaultFont", 16, "bold"))

        sticker_price_labels = ["TTM EPS", "Growth Rate (%)", "Future PE", "Margin of Safety (%)",
                                "Sticker Price no MOS", "Sticker Price with MOS"]
        sticker_price_entries = ["sticker_eps", "sticker_growth_rate", "sticker_future_pe",
                                 "sticker_calc_mos", "sticker_no_mos", "sticker_with_mos"]

        for i in range(4):
            label = tk.Label(sticker_calc_frame, text=sticker_price_labels[i])
            label.grid(row=i + 1, column=0)

            entry = tk.Entry(sticker_calc_frame, width=7)
            setattr(self, sticker_price_entries[i], entry)
            entry.grid(row=i + 1, column=1)

        sticker_calc_button = tk.Button(sticker_calc_frame, text="Calculate", command=self.calculate_sticker_price)
        sticker_calc_button.grid(columnspan=2, sticky="EW", pady=10)

        for i in range(4, 6):
            label = tk.Label(sticker_calc_frame, text=sticker_price_labels[i])
            label.grid(row=i + 2, column=0)

            entry = tk.Entry(sticker_calc_frame, width=12)
            setattr(self, sticker_price_entries[i], entry)
            entry.grid(row=i + 2, column=1)


def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
