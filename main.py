import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from ftfy import fix_encoding
import matplotlib.pyplot as plt
import pandas as pd
import os


def read_csv_file(file_name):
    rows = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0].__contains__('Bankbeziehung'):
                continue
            if row[0] == ';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;':
                break
            rows.append(row)
    return rows


def write_data_to_csv(iban, name, amount, currency):
    file_name = f"{name}_{iban}.csv"
    file_path = os.path.join('data', file_name)

    os.makedirs('data', exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write('Date,Amount,Currency\n')

    date = datetime.today().strftime('%Y-%m-%d')

    if not amount:
        amount = '0'
    amount = amount.replace('\'', '').replace(',', '.')

    with open(file_path, 'r') as file:
        data = file.readlines()
        for line in data:
            if line.startswith(date):
                print(f"Data for {date} already exists in {file_name}")
                continue

    with open(file_path, 'a') as file:
        file.write(f"{date},{amount},{currency}\n")
        print(f"Data written to {file_name}")

    refresh_accounts()


def on_drop(event):
    file_path = event.data.strip('{}')
    info = read_csv_file(file_path)

    for row in info:
        account_infos = fix_encoding(row[0]).split(';')
        write_data_to_csv(account_infos[0], account_infos[13], account_infos[27], account_infos[4])


def show_plot(selected_file):
    file_path = f'data/{selected_file}'
    data = pd.read_csv(file_path)

    data['Date'] = pd.to_datetime(data['Date'])

    data.sort_values('Date', inplace=True)

    plt.figure(figsize=(10, 5))  # Optional: Adjust the figure size for better readability
    plt.plot(data['Date'], data['Amount'])
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.title(f'Financial Data for {selected_file}')

    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.AutoDateLocator())
    plt.gcf().autofmt_xdate()  # Rotate date labels for better readability

    plt.show()


def get_available_accounts():
    available_accounts = []
    for file in os.listdir('data'):
        if file.endswith('.csv'):
            available_accounts.append(file)

    if not available_accounts:
        available_accounts.append('No accounts found')

    return available_accounts


def refresh_accounts():
    accounts = get_available_accounts()
    dropdown['values'] = accounts
    dropdown.current(0)
    update_current_label()


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        info = read_csv_file(file_path)
        for row in info:
            account_infos = fix_encoding(row[0]).split(';')
            write_data_to_csv(account_infos[0], account_infos[13], account_infos[27], account_infos[4])


def update_current_label(*args):
    try:
        current_value = dropdown.get()
        account_name_label.config(text=f"{current_value.split('_')[0]}", background='white', foreground='black')
        file_path = f'data/{current_value}'
        data = pd.read_csv(file_path)

        if 'Amount' not in data.columns:
            raise KeyError("'Amount' column not found in the data")

        if len(data) < 2:
            raise IndexError("Not enough data to calculate change")

        account_value = data['Amount'].iloc[-1]
        current_value_label.config(text=f"Value: {account_value}", background='white', foreground='black')

        account_change = data['Amount'].iloc[-1] - data['Amount'].iloc[-2]
        change_color = 'black'
        if account_change > 0:
            change_color = 'green'
        elif account_change < 0:
            change_color = 'red'

        current_change_label.config(text=f"Change: {account_change}", background='white', foreground=change_color)

    except FileNotFoundError:
        current_value_label.config(text="Error: File not found", background='red', foreground='black')
        current_change_label.config(text="Error: File not found", background='red', foreground='black')
    except pd.errors.EmptyDataError:
        current_value_label.config(text="Error: No data in file", background='red', foreground='black')
        current_change_label.config(text="Error: No data in file", background='red', foreground='black')
    except KeyError as e:
        current_value_label.config(text=f"Error: {e}", background='red', foreground='black')
        current_change_label.config(text=f"Error: {e}", background='red', foreground='black')
    except IndexError as e:
        current_value_label.config(text=f"Error: {e}", background='red', foreground='black')
        current_change_label.config(text=f"Error: {e}", background='red', foreground='black')
    except Exception as e:
        current_value_label.config(text=f"Error: {str(e)}", background='red', foreground='black')
        current_change_label.config(text=f"Error: {str(e)}", background='red', foreground='black')

def show_daily_report():
    report_window = tk.Toplevel()
    report_window.title('Daily Report')
    report_window.geometry('150x110')

#     report shows daily change and the total amount of money in all accounts of the day
    daily_change = 0
    total_amount = 0

    for file in os.listdir('data'):
        if file.endswith('.csv'):
            file_path = f'data/{file}'
            data = pd.read_csv(file_path)

            if len(data) < 2:
                continue

            daily_change += data['Amount'].iloc[-1] - data['Amount'].iloc[-2]
            total_amount += data['Amount'].iloc[-1]

    daily_change_label = ttk.Label(report_window, text=f"Daily Change: {daily_change}")
    daily_change_label.pack(pady=5)

    total_amount_label = ttk.Label(report_window, text=f"Total Amount: {total_amount}")
    total_amount_label.pack(pady=5)

    close_button = ttk.Button(report_window, text="Close", command=report_window.destroy)
    close_button.pack(pady=5)

    report_window.mainloop()


if __name__ == '__main__':
    root = TkinterDnD.Tk()
    root.title('CSV File Processor')
    root.geometry('600x250')

    main_frame = ttk.Frame(root, padding=(10, 10))
    main_frame.grid(row=0, column=0, sticky=tk.NSEW)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)

    label = ttk.Label(main_frame, text="Drag and drop a CSV file here", anchor="center", padding=(10, 10),
                      background="lightgrey")
    label.grid(row=0, column=2, rowspan=3, sticky=tk.NSEW)

    select_button = ttk.Button(label, text="Select File", command=select_file)
    select_button.pack(pady=5, padx=60)

    dropdown = ttk.Combobox(main_frame, values=get_available_accounts())
    dropdown.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
    dropdown.current(0)
    dropdown.bind("<<ComboboxSelected>>", update_current_label)

    changePanel = ttk.Label(main_frame, anchor="center", padding=(10, 10), background="white")
    changePanel.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

    account_name_label = ttk.Label(changePanel, text="Account: ")
    account_name_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

    current_value_label = ttk.Label(changePanel, text="Value: ")
    current_value_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

    current_change_label = ttk.Label(changePanel, text="Change: ")
    current_change_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

    plot_button = ttk.Button(main_frame, text="Show Plot", command=lambda: show_plot(dropdown.get()))
    plot_button.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

    refresh_button = ttk.Button(main_frame, text="Refresh", command=lambda: refresh_accounts())
    refresh_button.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

    daily_report_button = ttk.Button(main_frame, text="Daily Report", command=lambda: show_daily_report())
    daily_report_button.grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)

    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)

    refresh_accounts()
    root.mainloop()
