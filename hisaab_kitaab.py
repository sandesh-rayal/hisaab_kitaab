import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="💰 Hisaab-Kitaab", layout="wide")

# --- Helper ---
def get_user_file(username):
    os.makedirs("data", exist_ok=True)
    return os.path.join("data", f"{username.lower()}_transactions.csv")

# --- Login / Username ---
st.title("💰 Hisaab-Kitaab — Personal Budget Tracker")
username = st.text_input("Enter your name to continue:")
if not username:
    st.stop()

file_path = get_user_file(username)

# --- Load data ---
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    df = pd.DataFrame(columns=["Type", "Category", "Amount", "Date", "Description"])
    df.to_csv(file_path, index=False)

# --- Add new transaction ---
with st.expander("➕ Add New Transaction", expanded=True):
    col1, col2, col3, col4, col5 = st.columns(5)
    t_type = col1.selectbox("Type", ["Income", "Expense"])
    category = col2.selectbox("Category",
                              ["Salary", "Investments", "Food", "Rent", "Bills", "Entertainment", "Misc", "Other"])
    amount = col3.number_input("Amount (₹)", min_value=0.0, step=100.0)
    date = col4.date_input("Date", datetime.today())
    desc = col5.text_input("Description", "")

    if st.button("💾 Save Transaction"):
        new_data = pd.DataFrame([[t_type, category, amount, date, desc]],
                                columns=df.columns)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(file_path, index=False)
        st.success(f"{t_type} of ₹{amount:.2f} added under {category}!")

# --- Summary ---
st.subheader("📊 Summary Overview")

if df.empty:
    st.info("No transactions yet. Add your first one above!")
    st.stop()

total_income = df[df["Type"] == "Income"]["Amount"].sum()
total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
balance = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Income", f"₹{total_income:,.2f}")
col2.metric("💸 Total Expense", f"₹{total_expense:,.2f}")
col3.metric("💵 Balance", f"₹{balance:,.2f}")

# --- Monthly & Category Breakdown ---
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.to_period("M").astype(str)

selected_month = st.selectbox("📅 Select Month", sorted(df["Month"].unique(), reverse=True))
month_df = df[df["Month"] == selected_month]

exp_df = month_df[month_df["Type"] == "Expense"]
if not exp_df.empty:
    cat_sum = exp_df.groupby("Category")["Amount"].sum().reset_index()
    fig = px.pie(cat_sum, values="Amount", names="Category",
                 title=f"Category-wise Expenses for {selected_month}",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No expense data for this month.")

# --- Transaction History ---
st.subheader("🧾 Transaction History")
st.dataframe(
    df.sort_values("Date", ascending=False),
    use_container_width=True,
    hide_index=True
)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Transactions CSV", csv, "transactions.csv", "text/csv")
