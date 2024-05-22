import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from ftfy import fix_encoding
import matplotlib.pyplot as plt
import pandas as pd
import os


# Function to read the csv file
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


# Function to write data to a CSV file
def write_data_to_csv(iban, name, amount, currency):
    # File name is IBAN + Name + .csv
    file_name = f"{name}_{iban}.csv"
    file_path = f'data/{file_name}'

    # Ensure the file exists with headers if it does not already exist
    try:
        with open(file_path, 'r') as file:
            pass
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            file.write('Date,Amount,Currency\n')

    # Get current date
    date = datetime.today().strftime('%Y-%m-%d')

    if not amount:
        amount = '0'
    amount = amount.replace('\'', '').replace(',', '.')

    # Write data to file if the file does not already contain the data from the same day
    with open(file_path, 'a') as file:
        # Check if the data is already in the file
        with open(file_path, 'r') as file:
            data = file.readlines()
            for line in data:
                if line.startswith(date):
                    print(f"Data for {date} already exists in {file_name}")
                    return

        file.write(f"{date},{amount},{currency}\n")
        print(f"Data written to {file_name}")
        refresh_accounts()


# Function to handle file drop event
def on_drop(event):
    file_path = event.data.strip('{}')
    info = read_csv_file(file_path)

    for row in info:
        account_infos = fix_encoding(row[0]).split(';')
        write_data_to_csv(account_infos[0], account_infos[13], account_infos[27], account_infos[4])


def show_plot(selected_file):
    # read the file in the data folder
    file_path = f'data/{selected_file}'
    data = pd.read_csv(file_path)

    # plot the data into a line graph
    plt.plot(data['Date'], data['Amount'])
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.title(f'Amount vs Date for {selected_file}')
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


def select_file():
    # Function to open a file dialog to select a file
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        info = read_csv_file(file_path)
        for row in info:
            account_infos = fix_encoding(row[0]).split(';')
            write_data_to_csv(account_infos[0], account_infos[13], account_infos[27], account_infos[4])


# Main function to run the Tkinter application
if __name__ == '__main__':
    root = TkinterDnD.Tk()
    root.title('CSV File Processor')
    root.geometry('400x300')

    # Create a main frame to hold everything
    main_frame = ttk.Frame(root, padding=(10, 10))
    main_frame.grid(row=0, column=0, sticky=tk.NSEW)

    # Configure the grid layout
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)

    # Add label to instruct user inside the main frame (right side)
    label = ttk.Label(main_frame, text="Drag and drop a CSV file here", anchor="center", padding=(10, 10),
                      background="lightgrey")
    label.grid(row=0, column=2, rowspan=3, sticky=tk.NSEW)

    # Add button to within the label to select a file
    select_button = ttk.Button(label, text="Select File", command=select_file)
    select_button.pack(pady=5, padx=60)

    dropdown = ttk.Combobox(main_frame, values=get_available_accounts())
    dropdown.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
    dropdown.current(0)

    # Add button to show plot in the main frame (left side)
    plot_button = ttk.Button(main_frame, text="Show Plot", command=lambda: show_plot(dropdown.get()))
    plot_button.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

    # Add refresh button in the main frame (left side)
    refresh_button = ttk.Button(main_frame, text="Refresh", command=lambda: refresh_accounts())
    refresh_button.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

    # Set up drag-and-drop functionality
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)

    # Run the Tkinter event loop
    root.mainloop()
