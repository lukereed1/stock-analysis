import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import threading
import datetime
import json
import html as html_lib

# ==============================================================================
# 1. THE SCRAPER ENGINE
# ==============================================================================
class ScraperEngine:
    BASE_URL = "https://discountingcashflows.com/company/{}/"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }

    def __init__(self, status_callback):
        self.status_callback = status_callback

    def get_financials(self, ticker):
        ticker = ticker.upper()
        endpoints = [
            ("Income", "income-statement/"),
            ("Balance", "balance-sheet-statement/"),
            ("CashFlow", "cash-flow-statement/"),
            ("Ratios", "ratios/")
        ]
        
        merged_data = pd.DataFrame()
        current_price = 0.0
        total_steps = len(endpoints)
        
        for index, (name, slug) in enumerate(endpoints):
            percent = (index / total_steps)
            self.status_callback(f"Scraping {name}...", percent)

            url = self.BASE_URL.format(ticker) + slug
            try:
                print(f"Requesting: {url}")
                response = requests.get(url, headers=self.HEADERS, timeout=15)
                
                if response.status_code != 200:
                    print(f"⚠️ Failed to fetch {name}: {response.status_code}")
                    continue
                
                # Extract Price from the first page loaded
                if index == 0:
                    current_price = self._extract_price_from_html(response.text)

                df = self._parse_table(response.text)
                
                if not df.empty:
                    if merged_data.empty:
                        merged_data = df
                    else:
                        merged_data = pd.concat([merged_data, df], axis=1)
                        merged_data = merged_data.loc[:, ~merged_data.columns.duplicated()]
                        
            except Exception as e:
                print(f"Error scraping {name}: {e}")

        self.status_callback("Processing Data...", 0.9)
        
        if not merged_data.empty:
            merged_data.index.name = 'Date'
            return merged_data, current_price
            
        return None, 0.0

    def _extract_price_from_html(self, html_content):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            input_tag = soup.find('input', attrs={'x-init': lambda x: x and 'registerQuotePayload' in x})
            
            if input_tag and input_tag.has_attr('value'):
                raw_json = input_tag['value']
                clean_json = html_lib.unescape(raw_json)
                data = json.loads(clean_json)
                return float(data.get('price', 0.0))
        except:
            pass
        return 0.0

    def _parse_table(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', id='report-table')
        if not table: return pd.DataFrame()

        headers = []
        thead = table.find('thead')
        if thead:
            rows = thead.find_all('tr')
            if rows:
                cols = rows[-1].find_all(['th', 'td'])
                for col in cols[1:]: 
                    text = col.get_text(" ", strip=True).replace(" ", "-")
                    if "LTM" in text: text = "LTM"
                    headers.append(text)

        data = {}
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                name_span = row.find('span', class_='row-description-text')
                if name_span:
                    metric_name = name_span.get_text(strip=True)
                else:
                    cols = row.find_all(['td', 'th'])
                    if not cols: continue
                    metric_name = cols[0].get_text(strip=True)

                if not metric_name: continue

                row_values = []
                cols = row.find_all('td')
                value_cols = cols[1:] 

                for i, col in enumerate(value_cols):
                    if i >= len(headers): break
                    
                    val_attr = col.get('data-value')
                    final_val = np.nan
                    
                    if val_attr and val_attr != "":
                        try: final_val = float(val_attr)
                        except: pass
                    else:
                        val_text = col.get_text(strip=True)
                        final_val = self._clean_text_num(val_text)
                    
                    row_values.append(final_val)
                
                if any(pd.notna(x) for x in row_values):
                    if len(row_values) < len(headers):
                        row_values += [np.nan] * (len(headers) - len(row_values))
                    data[metric_name] = row_values[:len(headers)]

        return pd.DataFrame(data, index=headers)

    def _clean_text_num(self, text):
        if not text or text == '-': return np.nan
        text = text.upper().replace(',', '').replace('$', '').replace('%', '').replace('(', '-').replace(')', '')
        
        multiplier = 1
        if 'B' in text:
            multiplier = 1e9
            text = text.replace('B', '')
        elif 'M' in text:
            multiplier = 1e6
            text = text.replace('M', '')
        elif 'K' in text:
            multiplier = 1e3
            text = text.replace('K', '')
            
        try: 
            return float(text) * multiplier
        except: 
            return np.nan

# ==============================================================================
# 2. MATH ENGINE
# ==============================================================================
class FinancialMath:
    @staticmethod
    def calculate_cagr(current, past, years):
        if past is None or current is None or past <= 0 or current <= 0 or years == 0:
            return 0.0
        try:
            val = (current / past) ** (1 / years) - 1
            return round(val * 100, 2)
        except:
            return 0.0

    @staticmethod
    def get_col_fuzzy(df, keywords):
        df_cols = [str(c).strip() for c in df.columns]
        for k in keywords:
            k_lower = k.lower()
            for col in df_cols:
                if k_lower == col.lower():
                    return df.columns[df_cols.index(col)]
        for k in keywords:
            k_lower = k.lower()
            for col in df_cols:
                if k_lower in col.lower():
                    return df.columns[df_cols.index(col)]
        return None

    @staticmethod
    def get_growth_stats(df):
        search_map = {
            'Sales': ['Revenue', 'Total Revenue'],
            'EPS': ['Earnings Per Share (EPS)', 'Earnings Per Share'],
            'Equity': ["Total Stockholders' Equity", "Total Equity", "Book Value Per Share"],
            'FCF': ['Free Cash Flow'],
            'Shares': ['Weighted Average Shares Outstanding', 'Diluted Weighted Average Shares Outstanding', 'Shares Outstanding']
        }
        
        has_ltm = 'LTM' in df.index
        hist_df = df.drop('LTM', errors='ignore')
        stats = {}
        
        for key, keywords in search_map.items():
            col = FinancialMath.get_col_fuzzy(df, keywords)
            if col:
                display_current = 0
                if has_ltm:
                    try:
                        val = df.loc['LTM', col]
                        if pd.notna(val): display_current = val
                    except: pass
                
                series_hist = hist_df[col].dropna()
                if display_current == 0 and len(series_hist) > 0:
                    display_current = series_hist.iloc[0]

                try:
                    if len(series_hist) > 0:
                        curr_fy = series_hist.iloc[0]
                        if curr_fy == 0 and len(series_hist) > 1:
                            curr_fy = series_hist.iloc[1]

                        prev_1 = series_hist.iloc[1] if len(series_hist) > 1 else curr_fy
                        prev_5 = series_hist.iloc[5] if len(series_hist) > 5 else (series_hist.iloc[-1] if len(series_hist) > 0 else curr_fy)
                        prev_10 = series_hist.iloc[10] if len(series_hist) > 10 else (series_hist.iloc[-1] if len(series_hist) > 0 else curr_fy)
                        
                        stats[key] = {
                            'current': display_current,
                            '1y': FinancialMath.calculate_cagr(curr_fy, prev_1, 1),
                            '5y': FinancialMath.calculate_cagr(curr_fy, prev_5, 5),
                            '10y': FinancialMath.calculate_cagr(curr_fy, prev_10, 10),
                        }
                    else:
                        stats[key] = {'current': display_current, '1y':0, '5y':0, '10y':0}
                except:
                    stats[key] = {'current': display_current, '1y':0, '5y':0, '10y':0}
            else:
                stats[key] = {'current': 0, '1y':0, '5y':0, '10y':0}
        return stats

    @staticmethod
    def get_historic_ratios(df):
        ratio_map = {
            'ROIC': ['Return on Invested Capital', 'Return On Invested Capital'],
            'Debt/Equity': ['Debt to Equity Ratio', 'Debt to Equity'],
            'PE Ratio': ['Price to Earnings Ratio', 'PE Ratio']
        }
        clean_df = df.drop('LTM', errors='ignore')
        limit = 10
        results = {k: [] for k in ratio_map.keys()}
        results['Earnings Yield'] = []
        pe_series = []
        
        for label, keywords in ratio_map.items():
            col = FinancialMath.get_col_fuzzy(clean_df, keywords)
            extracted_values = []
            if col:
                raw_series = clean_df[col].dropna()
                valid_values = raw_series.head(limit).tolist()
                for raw in valid_values:
                    try:
                        val = float(raw)
                        extracted_values.append(round(val, 2))
                    except:
                        extracted_values.append(0)
            while len(extracted_values) < limit:
                extracted_values.append(0)
            results[label] = extracted_values
            if label == 'PE Ratio':
                pe_series = extracted_values

        yield_values = []
        for pe in pe_series:
            ey = 0
            if pe > 0: ey = round((1 / pe) * 100, 2)
            yield_values.append(ey)
        results['Earnings Yield'] = yield_values

        current_year = datetime.datetime.now().year
        results['Years'] = [current_year - i for i in range(1, limit + 1)]
        return results

    @staticmethod
    def calculate_dcf(fcf_per_share, growth_rate, discount_rate, terminal_multiple, margin_of_safety):
        try:
            g = growth_rate / 100
            d = discount_rate / 100
            fcf = fcf_per_share
            future_vals = []
            for i in range(1, 11):
                fcf = fcf * (1 + g)
                future_vals.append(fcf)
            
            pv_cash_flows = sum([val / ((1 + d) ** (i + 1)) for i, val in enumerate(future_vals)])
            terminal_val = future_vals[-1] * terminal_multiple
            pv_terminal = terminal_val / ((1 + d) ** 10)
            
            intrinsic_val = pv_cash_flows + pv_terminal
            buy_price = intrinsic_val * (1 - (margin_of_safety / 100))
            return intrinsic_val, buy_price
        except:
            return 0, 0

    @staticmethod
    def calculate_sticker_price(ttm_eps, growth_rate, future_pe, min_rate_return, margin_of_safety):
        try:
            g = growth_rate / 100
            r = min_rate_return / 100
            future_eps = ttm_eps * ((1 + g) ** 10)
            future_price = future_eps * future_pe
            sticker_price = future_price / ((1 + r) ** 10)
            buy_price = sticker_price * (1 - (margin_of_safety / 100))
            return sticker_price, buy_price
        except:
            return 0, 0

    @staticmethod
    def calculate_graham_formula(ttm_eps, growth_rate, margin_of_safety):
        try:
            value = ttm_eps * (8.5 + (2 * growth_rate))
            buy_price = value * (1 - (margin_of_safety / 100))
            return value, buy_price
        except:
            return 0, 0

# ==============================================================================
# 3. UI (Frontend)
# ==============================================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class StockApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.scraper = ScraperEngine(self.update_status)
        self.data_store = None 
        self.current_stock_price = 0.0
        
        self.title("Intrinsic Value Terminal")
        self.geometry("1300x850") 
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._init_sidebar()
        self._init_main_area()

    def _init_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="MARKET TERMINAL", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        self.entry_ticker = ctk.CTkEntry(self.sidebar, placeholder_text="Ticker (e.g. AAPL)")
        self.entry_ticker.pack(padx=20, pady=10)

        self.btn_search = ctk.CTkButton(self.sidebar, text="Scrape Data", height=40, command=self.start_scrape_thread)
        self.btn_search.pack(padx=20, pady=20)

        self.progress_label = ctk.CTkLabel(self.sidebar, text="Ready", font=ctk.CTkFont(size=12))
        self.progress_label.pack(pady=(10, 0))
        self.progress_bar = ctk.CTkProgressBar(self.sidebar)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=20, pady=5)

        self.frame_assumptions = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_assumptions.pack(padx=20, pady=30, fill="x")
        
        ctk.CTkLabel(self.frame_assumptions, text="VALUATION INPUTS", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self._add_input("Growth Rate (%)", "in_growth", "10")
        self._add_input("Future PE", "in_pe", "20")
        self._add_input("Discount Rate (%)", "in_disc", "15")
        self._add_input("Margin of Safety (%)", "in_mos", "50")
        
        self.btn_calc = ctk.CTkButton(self.frame_assumptions, text="Run Valuation", height=40, fg_color="green", command=self.calculate_valuations)
        self.btn_calc.pack(pady=20)

        # Info Button at bottom of sidebar
        self.btn_info = ctk.CTkButton(self.sidebar, text="Guide / Definitions", height=30, fg_color="#555555", command=self.open_info_window)
        self.btn_info.pack(side="bottom", pady=20, padx=20)

    def _add_input(self, text, attr, default):
        ctk.CTkLabel(self.frame_assumptions, text=text).pack(pady=(5,0), anchor="w")
        entry = ctk.CTkEntry(self.frame_assumptions)
        entry.insert(0, default)
        entry.pack(fill="x")
        setattr(self, attr, entry)

    def _init_main_area(self):
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.tab_metrics = self.tabs.add("Metrics & Growth")
        self.tab_val = self.tabs.add("Valuation Models")
        
        # -- METRICS TAB --
        # Changed from CTkScrollableFrame to CTkFrame to remove scrollbar
        self.tab_metrics_scroll = ctk.CTkFrame(self.tab_metrics, fg_color="transparent")
        self.tab_metrics_scroll.pack(fill="both", expand=True)

        self.header_frame = ctk.CTkFrame(self.tab_metrics_scroll, fg_color="transparent")
        self.header_frame.pack(pady=10)

        self.lbl_company = ctk.CTkLabel(self.header_frame, text="NO DATA LOADED", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_company.pack()
        self.lbl_price = ctk.CTkLabel(self.header_frame, text="Current Price: $0.00", font=ctk.CTkFont(size=18), text_color="#aaaaaa")
        self.lbl_price.pack()

        # 1. Growth Grid
        self.big4_frame = ctk.CTkFrame(self.tab_metrics_scroll)
        self.big4_frame.pack(fill="x", padx=10, pady=10)
        
        columns = ["Metric", "Current (LTM)", "1Yr Growth", "5Yr Growth", "10Yr Growth"]
        for i, col in enumerate(columns):
            ctk.CTkLabel(self.big4_frame, text=col, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=10, pady=5)
            self.big4_frame.grid_columnconfigure(i, weight=1)

        self.metric_widgets = {}
        rows = ["Sales", "EPS", "Equity", "FCF", "Shares"]
        for i, row in enumerate(rows):
            self.metric_widgets[row] = []
            ctk.CTkLabel(self.big4_frame, text=row).grid(row=i+1, column=0, pady=5)
            for j in range(4):
                lbl = ctk.CTkLabel(self.big4_frame, text="-")
                lbl.grid(row=i+1, column=j+1, pady=5)
                self.metric_widgets[row].append(lbl)

        # 2. Historical Ratios Table
        ctk.CTkLabel(self.tab_metrics_scroll, text="Historical Ratios (Last 10 Fiscal Years)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20,5))
        self.hist_ratios_frame = ctk.CTkFrame(self.tab_metrics_scroll)
        self.hist_ratios_frame.pack(fill="x", padx=10, pady=5)

        # -- VALUATION TAB --
        self.dcf_frame = ctk.CTkFrame(self.tab_val)
        self.dcf_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.lbl_val_price = ctk.CTkLabel(self.dcf_frame, text="Current Price: $0.00", font=ctk.CTkFont(size=22, weight="bold"), text_color="#F1C40F")
        self.lbl_val_price.pack(pady=10)
        
        ctk.CTkLabel(self.dcf_frame, text="--------------------------------").pack(pady=5)

        # Model 1
        ctk.CTkLabel(self.dcf_frame, text="Discounted Cash Flow (DCF)", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=5)
        self.lbl_dcf_val = ctk.CTkLabel(self.dcf_frame, text="Intrinsic Value: $0.00", font=ctk.CTkFont(size=16))
        self.lbl_dcf_val.pack()
        self.lbl_dcf_buy = ctk.CTkLabel(self.dcf_frame, text="Buy Price: $0.00", font=ctk.CTkFont(size=16, weight="bold"), text_color="#2CC985")
        self.lbl_dcf_buy.pack()

        ctk.CTkLabel(self.dcf_frame, text="--------------------------------").pack(pady=10)

        # Model 2
        ctk.CTkLabel(self.dcf_frame, text="Rule #1 Sticker Price", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=5)
        self.lbl_sticker_val = ctk.CTkLabel(self.dcf_frame, text="Sticker Price: $0.00", font=ctk.CTkFont(size=16))
        self.lbl_sticker_val.pack()
        self.lbl_sticker_buy = ctk.CTkLabel(self.dcf_frame, text="Buy Price: $0.00", font=ctk.CTkFont(size=16, weight="bold"), text_color="#2CC985")
        self.lbl_sticker_buy.pack()

        ctk.CTkLabel(self.dcf_frame, text="--------------------------------").pack(pady=10)

        # Model 3
        ctk.CTkLabel(self.dcf_frame, text="Benjamin Graham Formula", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=5)
        self.lbl_graham_val = ctk.CTkLabel(self.dcf_frame, text="Graham Value: $0.00", font=ctk.CTkFont(size=16))
        self.lbl_graham_val.pack()
        self.lbl_graham_buy = ctk.CTkLabel(self.dcf_frame, text="Buy Price: $0.00", font=ctk.CTkFont(size=16, weight="bold"), text_color="#2CC985")
        self.lbl_graham_buy.pack()

    # ---------------- INFO WINDOW ----------------
    def open_info_window(self):
        info_window = ctk.CTkToplevel(self)
        info_window.title("Guide & Definitions")
        info_window.geometry("600x700")
        
        # Make sure it stays on top
        info_window.attributes("-topmost", True)
        
        scroll = ctk.CTkScrollableFrame(info_window)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        def add_section(title, text):
            ctk.CTkLabel(scroll, text=title, font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x", pady=(15, 5))
            ctk.CTkLabel(scroll, text=text, font=ctk.CTkFont(size=13), justify="left", anchor="w", wraplength=540).pack(fill="x")

        # --- CONTENT ---
        intro = "This tool is designed for intrinsic value investing, helping you determine what a company is worth based on its fundamentals rather than stock price hype."
        add_section("Overview", intro)

        big4_text = (
            "1. Sales (Revenue): The money coming in from selling goods/services. Consistent growth proves demand.\n\n"
            "2. EPS (Earnings Per Share): Net profit divided by shares outstanding. Shows profitability per share.\n\n"
            "3. Equity (Book Value): Assets minus Liabilities. Growth in Book Value per share is often the best proxy for intrinsic value growth.\n\n"
            "4. FCF (Free Cash Flow): Operating Cash Flow minus Capital Expenditures. This is the 'real' cash the owner gets to keep."
        )
        add_section("The Big 4 Metrics", big4_text)

        growth_text = (
            "We analyze growth over 1 year, 5 years, and 10 years to find consistency. \n"
            "Ideally, we want to see >10% growth across all periods for Sales, EPS, Equity, and FCF."
        )
        add_section("Growth Rates", growth_text)

        ratios_text = (
            "ROIC (Return on Invested Capital): How efficiently management uses capital. >10% is good, >15% is excellent.\n\n"
            "Debt/Equity: Measures financial leverage. Lower is safer. < 0.5 is ideal.\n\n"
            "PE Ratio: Price you pay for $1 of earnings. Lower is better."
        )
        add_section("Key Ratios", ratios_text)

        val_text = (
            "1. DCF (Discounted Cash Flow): Projects future Free Cash Flow and discounts it back to today's dollars. Best for cash-cow businesses.\n\n"
            "2. Sticker Price (Rule #1): Projects future EPS growth multiplied by a future PE ratio, then discounted back by your desired return rate.\n\n"
            "3. Graham Formula: A quick heuristic by Ben Graham (Value = EPS * (8.5 + 2g)). Useful for a quick ballpark estimate."
        )
        add_section("Valuation Models", val_text)

        mos_text = (
            "The difference between the Intrinsic Value and the price you pay. \n"
            "A 50% Margin of Safety means you are buying a $100 bill for $50. This protects you against calculation errors and bad luck."
        )
        add_section("Margin of Safety (MOS)", mos_text)

    # ---------------- LOGIC ----------------
    def update_status(self, text, percent):
        self.after(0, lambda: self._update_status_main(text, percent))

    def _update_status_main(self, text, percent):
        self.progress_label.configure(text=text)
        self.progress_bar.set(percent)
        self.update_idletasks()

    def start_scrape_thread(self):
        ticker = self.entry_ticker.get()
        if not ticker: return
        
        self.btn_search.configure(state="disabled", text="Working...")
        self.update_idletasks()
        
        self.data_store = None 
        threading.Thread(target=self._scrape_worker, args=(ticker,), daemon=True).start()

    def _scrape_worker(self, ticker):
        df, price = self.scraper.get_financials(ticker)
        self.after(0, lambda: self._scrape_finished(df, price, ticker))

    def _scrape_finished(self, df, price, ticker):
        self.btn_search.configure(state="normal", text="Scrape Data")
        self.progress_label.configure(text="Idle")
        self.progress_bar.set(0)
        
        if df is None or df.empty:
            messagebox.showerror("Error", "No data found. Check Ticker or Internet.")
            return

        self.data_store = df
        self.current_stock_price = price
        
        self.lbl_company.configure(text=ticker.upper())
        self.lbl_price.configure(text=f"Current Price: ${price}")
        self.lbl_val_price.configure(text=f"Current Price: ${price}")

        stats = FinancialMath.get_growth_stats(df)
        self._populate_big4(stats)
        
        hist_ratios = FinancialMath.get_historic_ratios(df)
        self._populate_hist_ratios(hist_ratios)
        
        try:
            pe_vals = [x for x in hist_ratios['PE Ratio'] if x > 0]
            if pe_vals:
                avg_pe = sum(pe_vals) / len(pe_vals)
                self.in_pe.delete(0, "end")
                self.in_pe.insert(0, str(round(avg_pe, 2)))
        except:
            pass
        
        self.calculate_valuations()

    def _populate_big4(self, stats):
        def fmt(n):
            if abs(n) > 1e9: return f"{round(n/1e9, 2)}B"
            if abs(n) > 1e6: return f"{round(n/1e6, 2)}M"
            return str(round(n, 2))

        avg_roic = 0
        if self.data_store is not None:
            ratios = FinancialMath.get_historic_ratios(self.data_store)
            roic_vals = [r for r in ratios.get('ROIC', []) if r != 0]
            if roic_vals:
                recent = roic_vals[:5]
                avg_roic = sum(recent) / len(recent)

        for row_name, data in stats.items():
            if row_name not in self.metric_widgets: continue
            
            widgets = self.metric_widgets[row_name]
            widgets[0].configure(text=fmt(data['current']))
            
            for i, period in enumerate(['1y', '5y', '10y']):
                val = data[period]
                color = "white"
                
                if row_name == 'Shares':
                    if val <= -0.5: color = "#2CC985" 
                    elif val >= 1.0: color = "#ff5555"
                else:
                    if val >= 10: color = "#2CC985"
                    elif val < 0: color = "#ff5555"
                    if row_name == 'Equity' and val < 10:
                        shares_growth = stats.get('Shares', {}).get(period, 0)
                        if shares_growth <= -0.5 and avg_roic >= 10:
                            color = "#3498db" 

                widgets[i+1].configure(text=f"{val}%", text_color=color)

    def _populate_hist_ratios(self, data):
        for widget in self.hist_ratios_frame.winfo_children():
            widget.destroy()

        years = data['Years']
        metrics = ['ROIC', 'Earnings Yield', 'Debt/Equity', 'PE Ratio']

        ctk.CTkLabel(self.hist_ratios_frame, text="Metric", font=ctk.CTkFont(weight="bold"), fg_color="#333333", corner_radius=4).grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        self.hist_ratios_frame.grid_columnconfigure(0, weight=1)

        for i, yr in enumerate(years):
            ctk.CTkLabel(self.hist_ratios_frame, text=str(yr), font=ctk.CTkFont(weight="bold"), fg_color="#333333", corner_radius=4).grid(row=0, column=i+1, padx=2, pady=2, sticky="nsew")
            self.hist_ratios_frame.grid_columnconfigure(i+1, weight=1)

        for r_idx, met in enumerate(metrics):
            ctk.CTkLabel(self.hist_ratios_frame, text=met).grid(row=r_idx+1, column=0, padx=2, pady=2, sticky="nsew")
            values = data[met]
            for c_idx, val in enumerate(values):
                color = "white"
                if met == 'ROIC' and val >= 10: color = "green"
                if met == 'Earnings Yield' and val >= 10: color = "green"
                if met == 'Debt/Equity' and val < 0.5: color = "green"

                ctk.CTkLabel(self.hist_ratios_frame, text=str(val), text_color=color).grid(row=r_idx+1, column=c_idx+1, padx=2, pady=2, sticky="nsew")

    def calculate_valuations(self):
        if self.data_store is None: return

        try:
            g = float(self.in_growth.get())
            pe = float(self.in_pe.get())
            disc = float(self.in_disc.get())
            mos = float(self.in_mos.get())

            fcf_per_share_col = FinancialMath.get_col_fuzzy(self.data_store, ['Free Cash Flow Per Share'])
            fcf_total_col = FinancialMath.get_col_fuzzy(self.data_store, ['Free Cash Flow'])
            shares_col = FinancialMath.get_col_fuzzy(self.data_store, ['Weighted Average Shares', 'Shares Outstanding'])
            eps_col = FinancialMath.get_col_fuzzy(self.data_store, ['Earnings Per Share'])

            ttm_fcf_per_share = 0
            ttm_eps = 0
            
            def get_val_safe(col_name):
                if not col_name: return 0
                if 'LTM' in self.data_store.index:
                    try:
                        val = self.data_store.loc['LTM', col_name]
                        if pd.notna(val) and val != 0: return float(val)
                    except: pass
                s = self.data_store[col_name].dropna()
                if not s.empty: return float(s.iloc[0])
                return 0

            if fcf_per_share_col:
                ttm_fcf_per_share = get_val_safe(fcf_per_share_col)

            if ttm_fcf_per_share == 0 and fcf_total_col and shares_col:
                val_fcf = get_val_safe(fcf_total_col)
                val_shares = get_val_safe(shares_col)
                if val_fcf != 0 and val_shares != 0:
                    if abs(val_fcf) < 1000000: val_fcf *= 1000000 
                    if val_shares < 10000000: val_shares *= 1000000 
                    ttm_fcf_per_share = val_fcf / val_shares

            if eps_col:
                ttm_eps = get_val_safe(eps_col)

            dcf_val, dcf_buy = FinancialMath.calculate_dcf(ttm_fcf_per_share, g, disc, pe, mos)
            self.lbl_dcf_val.configure(text=f"Intrinsic Value: ${round(dcf_val, 2)}")
            self.lbl_dcf_buy.configure(text=f"Buy Price (@{int(mos)}% MOS): ${round(dcf_buy, 2)}")

            sticker, sticker_buy = FinancialMath.calculate_sticker_price(ttm_eps, g, pe, disc, mos)
            self.lbl_sticker_val.configure(text=f"Rule #1 Sticker Price: ${round(sticker, 2)}")
            self.lbl_sticker_buy.configure(text=f"Buy Price (@{int(mos)}% MOS): ${round(sticker_buy, 2)}")

            graham, graham_buy = FinancialMath.calculate_graham_formula(ttm_eps, g, mos)
            self.lbl_graham_val.configure(text=f"Graham Value: ${round(graham, 2)}")
            self.lbl_graham_buy.configure(text=f"Buy Price (@{int(mos)}% MOS): ${round(graham_buy, 2)}")

        except Exception as e:
            messagebox.showerror("Math Error", str(e))

if __name__ == "__main__":
  app = StockApp()
  app.mainloop()