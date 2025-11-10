import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import os


# ---------- MAIN APP ----------
class BudgetTrackerApp:
    def __init__(self, root, file_path, username):
        self.root = root
        self.username = username.capitalize()
        self.file_path = file_path

        self.root.title(f"💰 Hisaab-Kitaab 📖 - {self.username}'s Ledger")
        self.root.geometry("950x850")
        self.root.configure(bg="#F5F7FA")

        # Title
        title = tk.Label(root, text=f"💰 Hisaab-Kitaab 📖\n({self.username})",
                         font=("Segoe UI", 20, "bold"),
                         fg="#2C3E50", bg="#F5F7FA")
        title.pack(pady=15)

        # --- Input Frame ---
        frame = tk.Frame(root, bg="#E8F0FE", bd=2, relief=tk.RIDGE)
        frame.pack(padx=20, pady=10, fill="x")

        # Transaction Type
        ttk.Label(frame, text="Transaction Type:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=10, pady=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(frame, textvariable=self.type_var,
                                       values=["Income", "Expense"], state="readonly", width=15)
        self.type_combo.grid(row=0, column=1, padx=10)
        self.type_combo.bind("<<ComboboxSelected>>", self.update_categories)

        # Category
        ttk.Label(frame, text="Category:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, padx=10, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(frame, textvariable=self.category_var, state="readonly", width=15)
        self.category_combo.grid(row=1, column=1, padx=10)

        # Amount
        ttk.Label(frame, text="Amount (₹):", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, padx=10, pady=5)
        self.amount_entry = ttk.Entry(frame, width=18)
        self.amount_entry.grid(row=2, column=1)

        # Date
        ttk.Label(frame, text="Date (YYYY-MM-DD):", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, padx=10, pady=5)
        self.date_entry = ttk.Entry(frame, width=18)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=3, column=1)

        # Description
        ttk.Label(frame, text="Description:", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, padx=10, pady=5)
        self.desc_entry = ttk.Entry(frame, width=18)
        self.desc_entry.grid(row=4, column=1)

        # Buttons
        ttk.Button(frame, text="➕ Add Transaction", command=self.add_transaction).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="📊 View Summary", command=self.view_summary).grid(row=6, column=0, columnspan=2, pady=5)

        # --- Month Selection ---
        month_frame = tk.Frame(root, bg="#F5F7FA")
        month_frame.pack(pady=5)
        ttk.Label(month_frame, text="Select Month:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)

        months = [datetime(2025, m, 1).strftime("%B") for m in range(1, 13)]
        self.month_var = tk.StringVar(value=datetime.today().strftime("%B"))
        self.month_combo = ttk.Combobox(month_frame, textvariable=self.month_var, values=months, state="readonly", width=15)
        self.month_combo.pack(side=tk.LEFT, padx=5)

        # Message Label
        self.msg_label = tk.Label(root, text="", fg="green", font=("Segoe UI", 10, "italic"), bg="#F5F7FA")
        self.msg_label.pack(pady=5)

        # Chart Frame
        self.chart_frame = tk.Frame(root, bg="#F5F7FA")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas ref holder
        self.canvas = None

    # -------- Category Options --------
    def update_categories(self, event=None):
        t_type = self.type_var.get()
        if t_type == "Income":
            cats = ["Salary", "Investments", "Other"]
        elif t_type == "Expense":
            cats = ["Food", "Rent", "Bills", "Entertainment", "Misc"]
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
            messagebox.showerror("❌ Error", "Amount must be numeric!")
            return

        new_entry = pd.DataFrame([[t_type.lower(), category, amount, date, desc]],
                                 columns=["type", "category", "amount", "date", "description"])
        new_entry.to_csv(self.file_path, mode='a', header=not os.path.exists(self.file_path), index=False)

        self.msg_label.config(text=f"✅ {t_type} added: ₹{amount:.2f} under {category}")
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    # -------- View Summary with Pie Chart --------
    def view_summary(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            messagebox.showinfo("📂 No Data", "No transactions yet!")
            return

        df = pd.read_csv(self.file_path)
        if df.empty:
            messagebox.showinfo("📂 No Data", "No transactions yet!")
            return

        # Filter by selected month
        selected_month = self.month_var.get()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['month_name'] = df['date'].dt.strftime("%B")
        month_df = df[df['month_name'] == selected_month]

        if month_df.empty:
            messagebox.showinfo("📅 No Data", f"No transactions for {selected_month}")
            return

        total_income = month_df[month_df['type'] == 'income']['amount'].sum()
        total_expense = month_df[month_df['type'] == 'expense']['amount'].sum()
        balance = total_income - total_expense

        summary_text = f"📅 {selected_month} Summary:\n💰 Income: ₹{total_income:.2f} | 💸 Expense: ₹{total_expense:.2f} | 💵 Balance: ₹{balance:.2f}"
        summary_label = tk.Label(self.chart_frame, text=summary_text, font=("Segoe UI", 11, "bold"),
                                 fg="#2C3E50", bg="#F5F7FA")
        summary_label.pack(pady=10)

        # Category-wise Expense Breakdown
        exp_df = month_df[month_df['type'] == 'expense'].groupby('category')['amount'].sum()

        if not exp_df.empty:
            fig, ax = plt.subplots(figsize=(5, 5))
            wedges, texts, autotexts = ax.pie(exp_df, labels=exp_df.index,
                                              autopct=lambda pct: f"{pct:.1f}%\n(₹{pct/100*exp_df.sum():.0f})",
                                              startangle=90, textprops={"fontsize": 9})
            ax.set_title(f"{selected_month} - Expense Breakdown 💹", fontsize=12)
            plt.tight_layout()

            # Embed in Tkinter
            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(pady=10)
        else:
            tk.Label(self.chart_frame, text="No expense data for this month!",
                     fg="gray", bg="#F5F7FA", font=("Segoe UI", 10)).pack(pady=20)


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
            messagebox.showinfo("🆕 Account Created", f"Welcome {username.capitalize()}! Your ledger is ready.")
        else:
            messagebox.showinfo("👋 Welcome Back", f"Welcome back, {username.capitalize()}!")

        self.root.destroy()
        main_root = tk.Tk()
        BudgetTrackerApp(main_root, file_path, username)
        main_root.mainloop()


# ---------- RUN APP ----------
if __name__ == "__main__":
    root = tk.Tk()
    LoginScreen(root)
    root.mainloop()
