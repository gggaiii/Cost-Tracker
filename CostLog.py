import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
import os

# Database setup and connection
def create_connection():
    db_path = os.path.join(os.path.expanduser('~'), 'CostLogData', 'C:\\GitHub\\CostLog\\expenses.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Ensure the directory exists
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
            amount REAL NOT NULL,
            pay_to TEXT NOT NULL,
            description TEXT,
            payment_method TEXT DEFAULT 'HSBC UK'
        )
    ''')
    # Add new column if not exist
    cursor.execute("PRAGMA table_info(expenses)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'payment_method' not in columns:
        cursor.execute('ALTER TABLE expenses ADD COLUMN payment_method TEXT DEFAULT "cash"')
    conn.commit()
    conn.close()

# Function to add an expense to the database
def add_expense():
    # Formulate the date string from the selected dropdown values
    date = f"{selected_year.get()}-{selected_month.get():02d}-{selected_day.get():02d}"
    amount = entry_amount.get()
    pay_to = entry_pay_to.get()
    description = entry_description.get()
    payment_method = payment_method_var.get()
    conn = create_connection()
    cursor = conn.cursor()
    query = 'INSERT INTO expenses (date, amount, pay_to, description, payment_method) VALUES (?, ?, ?, ?, ?)'
    cursor.execute(query, (date, amount, pay_to, description, payment_method))
    conn.commit()
    conn.close()
    expenses_list.insert(tk.END, f"{date} - £{amount} - {pay_to} - {description} - {payment_method}")
    # Clear the input fields
    entry_amount.delete(0, tk.END)
    entry_pay_to.delete(0, tk.END)
    entry_description.delete(0, tk.END)


# Function to view all expenses from the database
def view_expenses():
    expenses_list.delete(0, tk.END)  # Clear the listbox
    conn = create_connection()
    cursor = conn.cursor()
    query = 'SELECT date, amount, pay_to, description, payment_method FROM expenses ORDER BY date DESC'
    cursor.execute(query)
    for row in cursor.fetchall():
        expenses_list.insert(tk.END, f"{row[0]} - £{row[1]} - {row[2]} - {row[3]} - {row[4]}")
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

# UI elements for entering other expense details
label_amount = ttk.Label(root, text="Amount (£):")
label_amount.grid(row=1, column=0)
entry_amount = ttk.Entry(root)
entry_amount.grid(row=1, column=1, columnspan=3)

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
payment_method_var = tk.StringVar(value=payment_methods[1])  # Default to 'cash'
label_payment_method = ttk.Label(root, text="Payment Method:")
label_payment_method.grid(row=4, column=0)
payment_method_menu = ttk.Combobox(root, textvariable=payment_method_var, values=payment_methods, state="readonly")
payment_method_menu.grid(row=4, column=1, columnspan=3)

button_add = ttk.Button(root, text="Add Expense", command=add_expense)
button_add.grid(row=5, column=1)

button_view = ttk.Button(root, text="View Expenses", command=view_expenses)
button_view.grid(row=5, column=0)

# Listbox to display expenses
expenses_list = tk.Listbox(root, width=60)
expenses_list.grid(row=6, column=0, columnspan=4, sticky="we")

# Initialize the database
setup_database()

# Start the GUI event loop
root.mainloop()
