import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ---------- SETUP ----------
st.set_page_config(page_title="💰 Hisaab-Kitaab", page_icon="📖", layout="wide")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


# ---------- HELPER FUNCTIONS ----------
def get_file_path(username):
    return os.path.join(DATA_DIR, f"{username.lower()}_transactions.csv")


def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=["type", "category", "amount", "date", "description"])


def save_data(df, file_path):
    df.to_csv(file_path, index=False)


# ---------- LOGIN ----------
st.title("💰 Hisaab-Kitaab 📖")
st.markdown("### Your Personal Budget Tracker")

username = st.text_input("👤 Enter your name to continue:")
if not username:
    st.stop()

file_path = get_file_path(username)
df = load_data(file_path)

# ---------- SIDEBAR: ADD TRANSACTION ----------
st.sidebar.header("➕ Add Transaction")

t_type = st.sidebar.selectbox("Type", ["Income", "Expense"])
if t_type == "Income":
    categories = ["Salary", "Investments", "Other"]
else:
    categories = ["Food", "Rent", "Bills", "Entertainment", "Misc"]

category = st.sidebar.selectbox("Category", categories)
amount = st.sidebar.number_input("Amount (₹)", min_value=0.0, step=100.0)
date = st.sidebar.date_input("Date", datetime.today())
desc = st.sidebar.text_input("Description", "")

if st.sidebar.button("Add"):
    if amount <= 0:
        st.sidebar.error("Amount must be greater than 0.")
    else:
        new_entry = pd.DataFrame([[t_type.lower(), category, amount, date, desc]],
                                 columns=["type", "category", "amount", "date", "description"])
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df, file_path)
        st.sidebar.success(f"✅ {t_type} of ₹{amount:.2f} added under {category}.")


# ---------- SUMMARY ----------
st.subheader(f"📊 Summary for {username.capitalize()}")
if df.empty:
    st.info("No transactions yet. Add some using the sidebar!")
    st.stop()

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["month"] = df["date"].dt.strftime("%B")
df["year"] = df["date"].dt.year

col1, col2 = st.columns(2)
year_filter = col1.selectbox("Select Year", sorted(df["year"].dropna().unique(), reverse=True))
month_filter = col2.selectbox("Select Month", ["All"] + sorted(df["month"].dropna().unique(),
                                                              key=lambda x: datetime.strptime(x, "%B").month))

filtered_df = df[df["year"] == year_filter]
if month_filter != "All":
    filtered_df = filtered_df[filtered_df["month"] == month_filter]

if filtered_df.empty:
    st.warning("No transactions for this period.")
    st.stop()

total_income = filtered_df[filtered_df['type'] == 'income']['amount'].sum()
total_expense = filtered_df[filtered_df['type'] == 'expense']['amount'].sum()
balance = total_income - total_expense

st.markdown("### 💵 Balance Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Income", f"₹{total_income:,.2f}")
col2.metric("Expense", f"₹{total_expense:,.2f}")
col3.metric("Balance", f"₹{balance:,.2f}")


# ---------- CATEGORY BREAKDOWN ----------
st.subheader("📈 Category-wise Expense Breakdown")
exp_df = filtered_df[filtered_df['type'] == 'expense']

if not exp_df.empty:
    exp_sum = exp_df.groupby('category')['amount'].sum()
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(exp_sum, labels=exp_sum.index, autopct='%1.1f%%', startangle=90)
    ax.set_title("Expense Distribution")
    st.pyplot(fig)

    st.dataframe(exp_sum.reset_index().rename(columns={'category': 'Category', 'amount': 'Total (₹)'}))
else:
    st.info("No expenses found for the selected period.")


# ---------- TRANSACTION HISTORY ----------
st.subheader("📜 Transaction History")

sort_col = st.selectbox("Sort by", ["Date (Newest First)", "Date (Oldest First)", "Amount (High to Low)",
                                    "Amount (Low to High)"])
if sort_col == "Date (Newest First)":
    filtered_df = filtered_df.sort_values("date", ascending=False)
elif sort_col == "Date (Oldest First)":
    filtered_df = filtered_df.sort_values("date", ascending=True)
elif sort_col == "Amount (High to Low)":
    filtered_df = filtered_df.sort_values("amount", ascending=False)
else:
    filtered_df = filtered_df.sort_values("amount", ascending=True)

# Add index for selection
filtered_df = filtered_df.reset_index(drop=True)
filtered_df["ID"] = filtered_df.index + 1
display_df = filtered_df[["ID", "type", "category", "amount", "date", "description"]].rename(
    columns={"type": "Type", "category": "Category", "amount": "Amount (₹)",
             "date": "Date", "description": "Description"}
)

st.dataframe(display_df, use_container_width=True)

# ---------- DELETE FUNCTIONALITY ----------
st.markdown("### 🗑️ Delete Transaction")
delete_id = st.number_input("Enter Transaction ID to Delete", min_value=1, max_value=len(display_df), step=1)

if st.button("Delete Selected"):
    if 1 <= delete_id <= len(display_df):
        row_to_delete = filtered_df.iloc[delete_id - 1]
        df = df.drop(df[(df["type"] == row_to_delete["type"]) &
                        (df["category"] == row_to_delete["category"]) &
                        (df["amount"] == row_to_delete["amount"]) &
                        (df["date"] == row_to_delete["date"]) &
                        (df["description"] == row_to_delete["description"])].index)
        save_data(df, file_path)
        st.success(f"✅ Transaction ID {delete_id} deleted successfully.")
        st.rerun()
    else:
        st.error("Invalid Transaction ID.")
