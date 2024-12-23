import tkinter as tk
from tkinter import messagebox
from calcs import dcfa_calc, get_sticker_price, calculate_growth_rate, add_commas_to_num
from scraper import (get_income_statement, get_balance_sheet,
                     get_ratios, get_cash_flow_statement, get_ttm_income_statement,
                     get_analyst_5_year_growth_prediction)
from data_processing import (get_market_cap, get_years_available, get_company_name_and_price,
                             get_ttm_fcf, get_ttm_eps, get_sales_growth_rates,
                             get_eps_growth_rates, get_free_cash_flow_growth_rates,
                             get_equity_growth_rates, get_roic, get_pe_ratio,
                             get_price_fcf_ratio, get_debt_equity_ratio)
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class StockAnalysis:
    def __init__(self, root):
        self.root = root
        self.scraping = False
        root.title("Stock Analysis")
        root.geometry("1000x650")
        self.create_gui_sections()

    # Creating Layout
    def create_gui_sections(self):
        self.create_search_bar_section()
        self.create_business_summary_section()
        self.create_historic_data_section()
        self.create_calculations_section()

    def create_search_bar_section(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=20)
        search_label = tk.Label(search_frame, text="Enter Stock Ticker:")
        search_label.grid(row=0, column=0, padx=5)

        search_entry = tk.Entry(search_frame)
        setattr(self, "search_bar", search_entry)
        search_entry.grid(row=0, column=1, padx=5)

        search_button = tk.Button(search_frame, text="Search", command=self.handle_search)
        search_button.grid(row=0, column=2, padx=5)

    def create_business_summary_section(self):
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

    def create_historic_data_section(self):
        historic_data_frame = tk.Frame(self.root)
        historic_data_frame.pack(pady=20)
        self.create_growth_data_table(historic_data_frame)
        self.create_ratio_data_table(historic_data_frame)

    def create_growth_data_table(self, historic_data_frame):
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

        self.create_growth_data_entries(growth_rates_frame)
        self.create_graph_button(1, 4, growth_rates_frame, self.handle_equity_graph_button)
        self.create_graph_button(2, 4, growth_rates_frame, self.handle_eps_graph_button)
        self.create_graph_button(3, 4, growth_rates_frame, self.handle_sales_graph_button)
        self.create_graph_button(4, 4, growth_rates_frame, self.handle_fcf_graph_button)

    def create_growth_data_entries(self, growth_rates_frame):
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

    def create_ratio_data_table(self, historic_data_frame):
        ratios_frame = tk.Frame(historic_data_frame)
        ratios_frame.pack(padx=(25, 0), side=tk.RIGHT)
        ratio_labels = ["ROIC (%)", "PE Ratio", "P/FCF Ratio", "Debt/Equity Ratio"]
        time_labels = ["1 Year", "5 Year", "10 Year"]

        for i in range(len(time_labels)):
            label = tk.Label(ratios_frame, text=time_labels[i])
            if i == 1:
                label.grid(row=0, column=i + 1, pady=(0, 10), padx=10)
            else:
                label.grid(row=0, column=i + 1, pady=(0, 10))

        for i in range(len(ratio_labels)):
            label = tk.Label(ratios_frame, text=ratio_labels[i])
            label.grid(row=i + 1, column=0, padx=(0, 10))

        self.create_ratio_data_entries(ratios_frame)
        self.create_graph_button(1, 4, ratios_frame, self.handle_roic_graph_button)
        self.create_graph_button(2, 4, ratios_frame, self.handle_pe_graph_button)
        self.create_graph_button(3, 4, ratios_frame, self.handle_p_fcf_graph_button)
        self.create_graph_button(4, 4, ratios_frame, self.handle_debt_equity_graph_button)

    def create_ratio_data_entries(self, ratio_frame):
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

    def create_calculations_section(self):
        calc_frame = tk.Frame(self.root)
        calc_frame.pack(pady=20)
        self.create_growth_calculator(calc_frame)
        self.create_dcfa_calculator(calc_frame)
        self.create_sticker_price_calculator(calc_frame)

    def create_growth_calculator(self, calc_frame):
        growth_calc_frame = tk.Frame(calc_frame)
        growth_calc_frame.grid(row=0, column=0, padx=(0, 25))
        self.create_sub_header(growth_calc_frame, "Growth Rate Calculator")
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

        self.create_calculate_button(growth_calc_frame, self.calculate_growth_rate, 4)

    def create_dcfa_calculator(self, calc_frame):
        dcfa_calc_frame = tk.Frame(calc_frame)
        dcfa_calc_frame.grid(row=0, column=1, padx=50)
        self.create_sub_header(dcfa_calc_frame, "Discounted Cash Flow Analysis")
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

        self.create_calculate_button(dcfa_calc_frame, self.calculate_dcfa, 5)

        for i in range(4, 6):
            label = tk.Label(dcfa_calc_frame, text=dcfa_labels[i])
            label.grid(row=i + 2, column=0)

            entry = tk.Entry(dcfa_calc_frame, width=12)
            setattr(self, dcfa_entries[i], entry)
            entry.grid(row=i + 2, column=1)

    def create_sticker_price_calculator(self, calc_frame):
        sticker_calc_frame = tk.Frame(calc_frame)
        sticker_calc_frame.grid(row=0, column=2, padx=(0, 10))
        self.create_sub_header(sticker_calc_frame, "Sticker Price")
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

        self.create_calculate_button(sticker_calc_frame, self.calculate_sticker_price, 5)

        for i in range(4, 6):
            label = tk.Label(sticker_calc_frame, text=sticker_price_labels[i])
            label.grid(row=i + 2, column=0)

            entry = tk.Entry(sticker_calc_frame, width=12)
            setattr(self, sticker_price_entries[i], entry)
            entry.grid(row=i + 2, column=1)

    #  Button click handlers
    def handle_search(self):
        if self.scraping:
            return
        search_value = getattr(self, "search_bar").get().upper()
        if not search_value.strip():
            self.popup_message("Enter a valid ticker")
        stock = self.get_stock_info(search_value)
        if not stock:
            return
        self.set_calculators()

    def handle_equity_graph_button(self):
        try:
            equity_map = self.create_data_map("historic_equity")
        except AttributeError:
            self.popup_message("Search a business first")
            return
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"Equity Chart for {company_name}",
            "Year",
            "Equity (Millions)",
            equity_map
        )

    def handle_eps_graph_button(self):
        try:
            eps_map = self.create_data_map("historic_eps")
        except AttributeError:
            self.popup_message("Search a business first")
            return
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"EPS Chart for {company_name}",
            "Year",
            "EPS",
            eps_map
        )

    def handle_sales_graph_button(self):
        try:
            sales_map = self.create_data_map("historic_sales")
        except AttributeError:
            self.popup_message("Search a business first")
            return
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"Sales Chart for {company_name}",
            "Year",
            "Sales (Millions)",
            sales_map
        )

    def handle_fcf_graph_button(self):
        try:
            fcf_map = self.create_data_map("historic_cash")
        except AttributeError:
            self.popup_message("Search a business first")
            return
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"Free Cash Flow Chart for {company_name}",
            "Year",
            "FCF (Millions)",
            fcf_map
        )

    def handle_roic_graph_button(self):
        try:
            roic_map = self.create_data_map("historic_roic")
        except AttributeError:
            self.popup_message("Search a business first")
            return
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"ROIC (%) Chart for {company_name}",
            "Year",
            "ROIC (%)",
            roic_map
        )

    def handle_pe_graph_button(self):
        try:
            pe_map = self.create_data_map("historic_pe")
        except AttributeError:
            self.popup_message("Search a business first")
            return
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"PE Ratio Chart for {company_name}",
            "Year",
            "PE Ratio",
            pe_map
        )

    def handle_p_fcf_graph_button(self):
        try:
            p_fcf_map = self.create_data_map("historic_p_fcf")
        except AttributeError:
            self.popup_message("Search a business first")
            return
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"P/FCF Ratio Chart for {company_name}",
            "Year",
            "Price/FCF Ratio",
            p_fcf_map
        )

    def handle_debt_equity_graph_button(self):
        try:
            debt_equity_map = self.create_data_map("historic_debt_equity")
        except AttributeError:
            self.popup_message("Search a business first")
            return
        company_name = getattr(self, "name_data").get()

        self.show_chart(
            f"Debt/Equity Ratio Chart for {company_name}",
            "Year",
            "Debt/Equity Ratio",
            debt_equity_map
        )

    def create_data_map(self, metric):
        data_map = {}
        historic_data = getattr(self, metric)

        year_list = getattr(self, "year_list")
        for i in range(len(year_list)):
            data_map[year_list[i]] = historic_data[i]

        return data_map

    #  Get/set
    def get_stock_info(self, ticker):
        self.scraping = True
        ttm_income_statement = get_ttm_income_statement(ticker)
        not_found = ttm_income_statement.find("div", string="Page Not Found - 404")
        if not_found:
            print("Stock not found")
            self.scraping = False
            return False
        income_statement = get_income_statement(ticker)
        balance_sheet = get_balance_sheet(ticker)
        ratios_and_metrics = get_ratios(ticker)
        cash_flow_statement = get_cash_flow_statement(ticker)
        analyst_estimated_growth = get_analyst_5_year_growth_prediction(ticker)
        self.scraping = False
        print("Scraping complete")
        years_available, year_list = get_years_available(income_statement)
        setattr(self, "year_list", year_list)
        self.set_summary(ttm_income_statement, analyst_estimated_growth)
        self.set_growth(income_statement, balance_sheet, years_available, cash_flow_statement)
        self.set_ratios(ratios_and_metrics, years_available)
        return True

    def set_entry_data(self, entry_name, data):
        entry = getattr(self, entry_name)
        entry.delete(0, tk.END)
        entry.insert(0, data)

    def set_calculators(self):
        analsyt_est_growth = getattr(self, "est_growth_data").get()
        analsyt_est_growth = analsyt_est_growth.replace("%", "")
        ttm_fcf = getattr(self, "fcf_data").get()
        ttm_fcf = ttm_fcf.replace(",", "")
        p_fcf_avg = getattr(self, "ten_year_p_fcf").get()
        ttm_eps = getattr(self, "eps_data").get()
        pe_avg = getattr(self, "ten_year_pe").get()
        self.set_entry_data("dcfa_growth_rate", analsyt_est_growth)
        self.set_entry_data("dcfa_ttm_fcf", ttm_fcf)
        self.set_entry_data("dcfa_p_fcf", p_fcf_avg)
        self.set_entry_data("dcfa_mos", 50)
        self.set_entry_data("sticker_eps", ttm_eps)
        self.set_entry_data("sticker_growth_rate", analsyt_est_growth)
        self.set_entry_data("sticker_future_pe", pe_avg)
        self.set_entry_data("sticker_calc_mos", 50)
        self.set_entry_data("intrin_no_mos", "")
        self.set_entry_data("intrin_with_mos", "")
        self.set_entry_data("sticker_no_mos", "")
        self.set_entry_data("sticker_with_mos", "")

    def set_summary(self, ttm_income_statement, analyst_growth_est):
        name, price = get_company_name_and_price(ttm_income_statement)
        market_cap = get_market_cap(ttm_income_statement, price)
        ttm_fcf = get_ttm_fcf(ttm_income_statement)
        ttm_eps = get_ttm_eps(ttm_income_statement)

        self.set_entry_data("name_data", name)
        self.set_entry_data("est_growth_data", analyst_growth_est)
        self.set_entry_data("cap_data", market_cap)
        self.set_entry_data("price_data", price)
        self.set_entry_data("fcf_data", ttm_fcf)
        self.set_entry_data("eps_data", ttm_eps)

    def set_growth(self, income_statement, balance_sheet, years_available, cash_flow_statement):
        equity_averages, all_equity = get_equity_growth_rates(balance_sheet, years_available)
        setattr(self, "historic_equity", all_equity)
        self.set_entry_data("one_year_equity", equity_averages[0])
        self.set_entry_data("five_year_equity", equity_averages[1])
        self.set_entry_data("ten_year_equity", equity_averages[2])

        eps_averages, all_eps = get_eps_growth_rates(income_statement, years_available)
        setattr(self, "historic_eps", all_eps)
        self.set_entry_data("one_year_eps", eps_averages[0])
        self.set_entry_data("five_year_eps", eps_averages[1])
        self.set_entry_data("ten_year_eps", eps_averages[2])

        sales_averages, all_sales = get_sales_growth_rates(income_statement, years_available)
        setattr(self, "historic_sales", all_sales)
        self.set_entry_data("one_year_sales", sales_averages[0])
        self.set_entry_data("five_year_sales", sales_averages[1])
        self.set_entry_data("ten_year_sales", sales_averages[2])

        cash_averages, all_cash = get_free_cash_flow_growth_rates(cash_flow_statement, years_available)
        setattr(self, "historic_cash", all_cash)
        self.set_entry_data("one_year_cash", cash_averages[0])
        self.set_entry_data("five_year_cash", cash_averages[1])
        self.set_entry_data("ten_year_cash", cash_averages[2])

    def set_ratios(self, ratios_and_metrics, years_available):
        roic_averages, all_roic = get_roic(ratios_and_metrics, years_available)
        setattr(self, "historic_roic", all_roic)
        self.set_entry_data("ttm_roic", roic_averages[0])
        self.set_entry_data("five_year_roic", roic_averages[1])
        self.set_entry_data("ten_year_roic", roic_averages[2])

        pe_averages, all_pe = get_pe_ratio(ratios_and_metrics, years_available)
        setattr(self, "historic_pe", all_pe)
        self.set_entry_data("ttm_pe", pe_averages[0])
        self.set_entry_data("five_year_pe", pe_averages[1])
        self.set_entry_data("ten_year_pe", pe_averages[2])

        p_fcf_averages, all_p_fcf = get_price_fcf_ratio(ratios_and_metrics, years_available)
        setattr(self, "historic_p_fcf", all_p_fcf)
        self.set_entry_data("ttm_p_fcf", p_fcf_averages[0])
        self.set_entry_data("five_year_p_fcf", p_fcf_averages[1])
        self.set_entry_data("ten_year_p_fcf", p_fcf_averages[2])

        debt_equity_averages, all_debt_equity = get_debt_equity_ratio(ratios_and_metrics, years_available)
        setattr(self, "historic_debt_equity", all_debt_equity)
        self.set_entry_data("ttm_d_fcf", debt_equity_averages[0])
        self.set_entry_data("five_year_d_fcf", debt_equity_averages[1])
        self.set_entry_data("ten_year_d_fcf", debt_equity_averages[2])

    # Calcs
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
        self.set_entry_data("calc_growth_rate", growth_rate)

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
        self.set_entry_data("intrin_no_mos", add_commas_to_num(intrinsic_value) + "M")
        self.set_entry_data("intrin_with_mos", add_commas_to_num(intrinsic_value_with_mos) + "M")

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
        self.set_entry_data("sticker_no_mos", current_price)
        self.set_entry_data("sticker_with_mos", current_price_with_mos)

    # Util
    @staticmethod
    def create_graph_button(row, col, frame, command):
        button = tk.Button(frame, text=">", command=command)
        button.grid(row=row, column=col)

    @staticmethod
    def create_calculate_button(frame, command, row):
        dcfa_calc_button = tk.Button(frame, text="Calculate", command=command)
        dcfa_calc_button.grid(row=row, columnspan=2, sticky="EW", pady=10)

    @staticmethod
    def create_sub_header(frame, text):
        sticker_price_calc_label = tk.Label(frame, text=text)
        sticker_price_calc_label.grid(row=0, columnspan=2, sticky="EW", pady=(0, 10), padx=(20, 0))
        sticker_price_calc_label.config(font=("tkDefaultFont", 16, "bold"))

    def show_chart(self, title, x_title, y_title, data_map):
        x_data = list(data_map.keys())[::-1]
        y_data = list(data_map.values())[::-1]
        graph_window = self.create_new_window(title)
        fig = Figure(figsize=(8, 5), dpi=100)

        plot = fig.add_subplot(111)
        plot.bar(x_data, y_data, color="blue", width=0.7)
        plot.set_xlabel(x_title)
        plot.set_ylabel(y_title)
        plot.set_title(title)

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        toolbar = NavigationToolbar2Tk(canvas, graph_window)
        toolbar.update()
        canvas.get_tk_widget().pack()

    def create_new_window(self, title):
        new_window = tk.Toplevel(self.root)
        new_window.title(title)
        return new_window

    @staticmethod
    def popup_message(message):
        messagebox.showinfo("Error", message)


def main():
    root = tk.Tk()
    try:
        root.tk.call('tk', 'windowingsystem')
    except tk.TclError:
        pass

    app = StockAnalysis(root)
    root.mainloop()


if __name__ == '__main__':
    main()
