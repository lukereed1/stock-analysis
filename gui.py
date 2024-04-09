import tkinter as tk


class GUI:
    def __init__(self, root):
        self.root = root
        root.title("Stock Analysis")
        root.geometry("1000x650")
        self.create_widgets()

    def set_data(self, entry_name, data):
        entry = getattr(self, entry_name)
        entry.delete(0, tk.END)
        entry.insert(0, data)
        print(entry)

    def create_widgets(self):
        self.search_bar()
        self.business_summary()
        self.historic_data()
        self.calculations_section()
        self.set_data("growth_rate", "BIG REEDOS")
        self.set_data("years", "BIG REEDOS")

    def search_bar(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=20)

        search_label = tk.Label(search_frame, text="Enter Stock Ticker:")
        search_label.grid(row=0, column=0, padx=5)

        search_entry = tk.Entry(search_frame)
        search_entry.grid(row=0, column=1, padx=5)

        search_button = tk.Button(search_frame, text="Search")
        search_button.grid(row=0, column=2, padx=5)

    def business_summary(self):
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
        ratio_labels = ["ROIC (%)", "PE Ratio", "P/FCF Ratio", "Debt/FCF Ratio"]
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
        self.growth_calc(calc_frame)

    def growth_calc(self, calc_frame):
        growth_calc_frame = tk.Frame(calc_frame)
        growth_calc_frame.grid(row=0, column=0, padx=(0, 50))
        growth_rate_calc_label = tk.Label(growth_calc_frame, text="Growth Rate Calculator")
        growth_rate_calc_label.grid(row=0, columnspan=2, sticky="EW", pady=(0, 10))
        growth_rate_calc_label.config(font=("TkDefaultFont", 16, "bold"))

        growth_calc_labels = ["Start Amount", "End Amount", "Years", "Growth Rate"]
        growth_calc_entries = ["start_amount", "end_amount", "years", "growth_rate"]
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

        growth_calc_button = tk.Button(growth_calc_frame, text="Calculate")
        growth_calc_button.grid(row=4, columnspan=2, sticky="EW", pady=10)

    def dcfa_calc(self, calc_frame):
        print("test")

    def sticker_price_calc(self, calc_frame):
        print("test")
def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
