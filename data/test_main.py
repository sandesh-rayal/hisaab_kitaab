import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import os


# ---------- MAIN APP CLASS ----------
class BudgetTrackerApp:
    def __init__(self, root, file_path, username):
        self.root = root
        self.username = username.capitalize()
        self.root.title(f"💰 Hisaab-Kitaab 📖- {self.username}'s Ledger")
        self.root.geometry("480x550")
        self.root.configure(bg="#F5F7FA")
        self.file_path = file_path

        # Title
        title = tk.Label(root, text=f"💰 Hisaab-Kitaab 📖\n({self.username})",
                         font=("Segoe UI", 20, "bold"),
                         fg="#2C3E50", bg="#F5F7FA")
        title.pack(pady=15)

        # Transaction Type
        tk.Label(root, text="Transaction Type:", bg="#F5F7FA").pack()
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(root, textvariable=self.type_var,
                                       values=["Income", "Expense"], state="readonly")
        self.type_combo.pack(pady=5)
        self.type_var.trace("w", self.update_categories)

        # Category
        tk.Label(root, text="Category:", bg="#F5F7FA").pack()
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(root, textvariable=self.category_var, state="readonly")
        self.category_combo.pack(pady=5)

        # Amount
        tk.Label(root, text="Amount:", bg="#F5F7FA").pack()
        self.amount_entry = tk.Entry(root)
        self.amount_entry.pack(pady=5)

        # Date
        tk.Label(root, text="Date (YYYY-MM-DD):", bg="#F5F7FA").pack()
        self.date_entry = tk.Entry(root)
        self.date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.date_entry.pack(pady=5)

        # Description
        tk.Label(root, text="Description:", bg="#F5F7FA").pack()
        self.desc_entry = tk.Entry(root, width=40)
        self.desc_entry.pack(pady=5)

        # Buttons
        tk.Button(root, text="➕ Add Transaction", command=self.add_transaction,
                  bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold"), width=20).pack(pady=10)
        tk.Button(root, text="📊 View Summary", command=self.view_summary,
                  bg="#2980B9", fg="white", font=("Segoe UI", 10, "bold"), width=20).pack(pady=5)

    # -------- Category Options --------
    def update_categories(self, *args):
        t_type = self.type_var.get().lower()
        if t_type == "income":
            cats = ["Salary", "Other"]
        elif t_type == "expense":
            cats = ["Food", "Rent", "Bills", "Misc"]
        else:
            cats = []
        self.category_combo['values'] = cats
        if cats:
            self.category_combo.current(0)

    # -------- Add Transaction --------
    def add_transaction(self):
        t_type = self.type_var.get()
        category = self.category_var.get()
        amount = self.amount_entry.get()
        date = self.date_entry.get()
        desc = self.desc_entry.get()

        if not all([t_type, category, amount]):
            messagebox.showwarning("⚠️ Missing Info", "Please fill all required fields!")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("❌ Error", "Amount must be a number!")
            return

        new_entry = pd.DataFrame([[t_type, category, amount, date, desc]],
                                 columns=["type", "category", "amount", "date", "description"])
        new_entry.to_csv(self.file_path, mode='a', header=not os.path.exists(self.file_path), index=False)

        messagebox.showinfo("✅ Success", f"Transaction added under {category}")
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    # -------- View Summary --------
    def view_summary(self):
        df = pd.read_csv(self.file_path)
        if df.empty:
            messagebox.showinfo("ℹ️ Info", "No transactions yet!")
            return

        total_income = df[df['type'] == 'Income']['amount'].sum()
        total_expense = df[df['type'] == 'Expense']['amount'].sum()
        balance = total_income - total_expense

        summary = (f"💼 {self.username}'s Summary\n\n"
                   f"Total Income : ₹{total_income:.2f}\n"
                   f"Total Expense: ₹{total_expense:.2f}\n"
                   f"Balance      : ₹{balance:.2f}")

        messagebox.showinfo("📊 Summary", summary)


# ---------- LOGIN SCREEN ----------
class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Login - Hisaab-Kitaab")
        self.root.geometry("350x250")
        self.root.configure(bg="#ECF0F1")

        tk.Label(root, text="📖 Hisaab-Kitaab", font=("Segoe UI", 18, "bold"),
                 fg="#2C3E50", bg="#ECF0F1").pack(pady=20)

        tk.Label(root, text="Enter your name:", bg="#ECF0F1").pack()
        self.username_entry = tk.Entry(root, font=("Segoe UI", 12))
        self.username_entry.pack(pady=10)

        tk.Button(root, text="🚀 Start Tracking", command=self.login_user,
                  bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold"), width=20).pack(pady=10)

    def login_user(self):
        username = self.username_entry.get().strip().lower()
        if not username:
            messagebox.showwarning("⚠️ Required", "Please enter your name!")
            return

        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, f"{username}_transactions.csv")

        if not os.path.exists(file_path):
            df = pd.DataFrame(columns=["type", "category", "amount", "date", "description"])
            df.to_csv(file_path, index=False)
            messagebox.showinfo("🆕 Account Created", f"Welcome {username.capitalize()}! Your new ledger is ready.")
        else:
            messagebox.showinfo("👋 Welcome Back", f"Welcome back, {username.capitalize()}!")

        # Close login and open main tracker
        self.root.destroy()
        main_root = tk.Tk()
        BudgetTrackerApp(main_root, file_path, username)
        main_root.mainloop()


# ---------- RUN APP ----------
if __name__ == "__main__":
    root = tk.Tk()
    LoginScreen(root)
    root.mainloop()
