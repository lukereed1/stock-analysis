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

    def create_widgets(self):
        self.search_bar_widget()
        self.summary_data_widget()
        self.set_data("name_data", "testing123")
        self.set_data("eps_data", "big reedos")

    def search_bar_widget(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=20)

        search_label = tk.Label(search_frame, text="Enter Stock Ticker:")
        search_label.grid(row=0, column=0, padx=5)

        search_entry = tk.Entry(search_frame)
        search_entry.grid(row=0, column=1, padx=5)

        search_button = tk.Button(search_frame, text="Search")
        search_button.grid(row=0, column=2, padx=5)

    def summary_data_widget(self):
        summary_frame = tk.Frame(self.root)
        summary_frame.pack(pady=10)
        labels = ["Business Name", "Analyst Est. Growth", "Market Cap", "Current Price", "TTM FCF", "TTM EPS"]
        entries = ["name_data", "est_growth_data", "cap_data", "price_data", "fcf_data", "eps_data"]

        col = 0
        for i in range(len(labels)):
            data_label = tk.Label(summary_frame, text=labels[i])
            data_label.grid(row=i % 2, column=col)

            data_entry = tk.Entry(summary_frame, width=15)
            setattr(self, entries[i], data_entry)
            data_entry.grid(row=i % 2, column=col + 1)

            if i % 2 == 1:
                col += 2


def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
