import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
import os

# Database setup and connection
def create_connection():
    # Define a fixed path for the database
    db_path = os.path.join('C:\\Database\\databases', 'expenses.db')  # Change the path to your own path
    conn = sqlite3.connect(db_path)
    return conn

def setup_database():
    conn = create_connection()
    cursor = conn.cursor()
    # Create table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            currency TEXT DEFAULT 'GBP',
            amount REAL NOT NULL,
            pay_to TEXT NOT NULL,
            description TEXT,
            payment_method TEXT DEFAULT 'HSBC UK'
        )
    ''')
    # Add currency column if it does not exist
    cursor.execute("PRAGMA table_info(expenses)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'currency' not in columns:
        cursor.execute('ALTER TABLE expenses ADD COLUMN currency TEXT DEFAULT "GBP"')
    conn.commit()
    conn.close()

# Function to add an expense to the database
def add_expense():
    date = f"{selected_year.get()}-{selected_month.get():02d}-{selected_day.get():02d}"
    currency = currency_var.get()
    amount = entry_amount.get()
    pay_to = entry_pay_to.get()
    description = entry_description.get()
    payment_method = payment_method_var.get()
    conn = create_connection()
    cursor = conn.cursor()
    query = 'INSERT INTO expenses (date, currency, amount, pay_to, description, payment_method) VALUES (?, ?, ?, ?, ?, ?)'
    cursor.execute(query, (date, currency, amount, pay_to, description, payment_method))
    conn.commit()
    conn.close()
    view_expenses()  # Refresh list after adding
    # Clear the input fields
    entry_amount.delete(0, tk.END)
    entry_pay_to.delete(0, tk.END)
    entry_description.delete(0, tk.END)

# Function to view all expenses from the database
sort_order = "DESC"
def toggle_sort_order():
    global sort_order
    sort_order = "ASC" if sort_order == "DESC" else "DESC"
    view_expenses()

def view_expenses():
    expenses_list.delete(0, tk.END)
    conn = create_connection()
    cursor = conn.cursor()
    query = f'''
        SELECT date, currency, amount, pay_to, description, payment_method 
        FROM expenses 
        ORDER BY date {sort_order}, currency
    '''
    cursor.execute(query)
    last_date = ""
    for row in cursor.fetchall():
        date_display = row[0] if row[0] != last_date else "----"
        expenses_list.insert(tk.END, f"{date_display} - {row[1]} - £{row[2]} - {row[3]} - {row[4]} - {row[5]}")
        last_date = row[0]
    conn.close()

# Search function
def search_expenses():
    search_query = search_entry.get()
    expenses_list.delete(0, tk.END)
    conn = create_connection()
    cursor = conn.cursor()
    query = f'''
        SELECT date, currency, amount, pay_to, description, payment_method
        FROM expenses
        WHERE date LIKE '%' || ? || '%' OR
              amount LIKE '%' || ? || '%' OR
              pay_to LIKE '%' || ? || '%' OR
              description LIKE '%' || ? || '%' OR
              payment_method LIKE '%' || ? || '%'
        ORDER BY date DESC
    '''
    cursor.execute(query, (search_query, search_query, search_query, search_query, search_query))
    for row in cursor.fetchall():
        expenses_list.insert(tk.END, f"{row[0]} - {row[1]} - £{row[2]} - {row[3]} - {row[4]} - {row[5]}")
    conn.close()

# Setting up the main window
root = tk.Tk()
root.title("Daily Expense Tracker")

# Dropdown for date selection
current_year = datetime.now().year
year_range = list(range(current_year, current_year - 10, -1))
month_range = list(range(1, 13))
day_range = list(range(1, 32))

selected_day = tk.IntVar(value=1)
selected_month = tk.IntVar(value=1)
selected_year = tk.IntVar(value=current_year)

label_date = ttk.Label(root, text="Date:")
label_date.grid(row=0, column=0)
day_menu = ttk.Combobox(root, textvariable=selected_day, values=day_range, width=5)
day_menu.grid(row=0, column=1)
month_menu = ttk.Combobox(root, textvariable=selected_month, values=month_range, width=5)
month_menu.grid(row=0, column=2)
year_menu = ttk.Combobox(root, textvariable=selected_year, values=year_range, width=5)
year_menu.grid(row=0, column=3)

# Currency selection
currencies = ['GBP', 'RMB', 'EUR', 'USD']
currency_var = tk.StringVar(value='GBP')
label_currency = ttk.Label(root, text="Currency:")
label_currency.grid(row=1, column=2)
currency_menu = ttk.Combobox(root, textvariable=currency_var, values=currencies, state="readonly")
currency_menu.grid(row=1, column=3)

# UI elements for entering other expense details
label_amount = ttk.Label(root, text="Amount (£):")
label_amount.grid(row=1, column=0)
entry_amount = ttk.Entry(root)
entry_amount.grid(row=1, column=1, columnspan=1)

label_pay_to = ttk.Label(root, text="Pay to:")
label_pay_to.grid(row=2, column=0)
entry_pay_to = ttk.Entry(root)
entry_pay_to.grid(row=2, column=1, columnspan=3)

label_description = ttk.Label(root, text="Description:")
label_description.grid(row=3, column=0)
entry_description = ttk.Entry(root)
entry_description.grid(row=3, column=1, columnspan=3)

# Payment method dropdown
payment_methods = ['cash', 'HSBC UK', 'HSBC Global', 'Barclay', 'Bank of China', 'China Merchant Bank']
payment_method_var = tk.StringVar(value=payment_methods[1])
label_payment_method = ttk.Label(root, text="Payment Method:")
label_payment_method.grid(row=4, column=0)
payment_method_menu = ttk.Combobox(root, textvariable=payment_method_var, values=payment_methods, state="readonly")
payment_method_menu.grid(row=4, column=1, columnspan=3)

button_add = ttk.Button(root, text="Add Expense", command=add_expense)
button_add.grid(row=5, column=1)

button_view = ttk.Button(root, text="View Expenses", command=view_expenses)
button_view.grid(row=5, column=0)

# Search functionality
search_entry = ttk.Entry(root)
search_entry.grid(row=6, column=0, columnspan=2)
search_button = ttk.Button(root, text="Search", command=search_expenses)
search_button.grid(row=6, column=2)

# Sort button
sort_button = ttk.Button(root, text="Toggle Sort Order", command=toggle_sort_order)
sort_button.grid(row=6, column=3)

# Listbox to display expenses
expenses_list = tk.Listbox(root, width=60)
expenses_list.grid(row=7, column=0, columnspan=4, sticky="we")

# Initialize the database
setup_database()

# Start the GUI event loop
root.mainloop()
