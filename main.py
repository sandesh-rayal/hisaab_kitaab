import csv
import os
import pandas as pd
from datetime import datetime

# ✅ Always use absolute paths based on this file’s location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FILE_PATH = os.path.join(DATA_DIR, "transactions.csv")

# ✅ Ensure the data folder exists
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Create CSV file if it doesn’t exist
if not os.path.exists(FILE_PATH):
    with open(FILE_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["type", "category", "amount", "date", "description"])


def add_transaction():
    while True:
        print("\nSelect transaction type:")
        print("1. Income")
        print("2. Expense")
        print("0. 🔙 Back")

        t_choice = input("Enter choice: ").strip()
        if t_choice == "0":
            return
        elif t_choice == "1":
            t_type = "income"
            categories = ["Salary", "Other"]
            break
        elif t_choice == "2":
            t_type = "expense"
            categories = ["Food", "Rent", "Bills", "Misc"]
            break
        else:
            print("⚠️ Invalid choice! Please try again.")

    while True:
        print(f"\nSelect {t_type} category:")
        for i, cat in enumerate(categories, start=1):
            print(f"{i}. {cat}")
        print("0. 🔙 Back")

        c_choice = input("Enter category number: ").strip()
        if c_choice == "0":
            return
        try:
            category = categories[int(c_choice) - 1]
            break
        except (ValueError, IndexError):
            print("⚠️ Invalid choice! Please try again.")

    try:
        amount = float(input("Enter amount: "))
    except ValueError:
        print("⚠️ Invalid amount! Transaction cancelled.")
        return

    date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip() or datetime.today().strftime('%Y-%m-%d')
    description = input("Enter description: ")

    with open(FILE_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([t_type, category, amount, date, description])

    print(f"✅ Transaction added successfully under category: {category}")


def view_summary():
    if not os.path.exists(FILE_PATH) or os.path.getsize(FILE_PATH) == 0:
        print("⚠️ No data found!")
        return

    df = pd.read_csv(FILE_PATH)
    if df.empty:
        print("⚠️ No transactions to show!")
        return

    total_income = df[df["type"] == "income"]["amount"].sum()
    total_expense = df[df["type"] == "expense"]["amount"].sum()
    balance = total_income - total_expense

    print("\n=== 💼 Summary ===")
    print(f"Total Income : ₹{total_income:.2f}")
    print(f"Total Expense: ₹{total_expense:.2f}")
    print(f"Balance      : ₹{balance:.2f}\n")

    if total_expense > 0:
        print("Expense by Category:")
        print(df[df["type"] == "expense"].groupby("category")["amount"].sum())


def main():
    while True:
        print("\n=== 💰 Budget Tracker ===")
        print("1. Add Transaction")
        print("2. View Summary")
        print("3. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_summary()
        elif choice == "3":
            print("👋 Exiting Budget Tracker. Goodbye!")
            break
        else:
            print("⚠️ Invalid choice! Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
