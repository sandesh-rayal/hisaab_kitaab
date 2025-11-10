import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="💰 Hisaab-Kitaab", page_icon="📖", layout="centered")

# -------------------- FILE HANDLING --------------------
DATA_FILE = "transactions.csv"

expected_cols = ["Type", "Category", "Amount", "Date", "Description"]

# Load data safely
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
        if df.empty or list(df.columns) != expected_cols:
            df = pd.DataFrame(columns=expected_cols)
    except Exception:
        df = pd.DataFrame(columns=expected_cols)
else:
    df = pd.DataFrame(columns=expected_cols)

# -------------------- APP HEADER --------------------
st.title("💰 Hisaab-Kitaab — Personal Budget Tracker")

# -------------------- USER INPUT --------------------
username = st.text_input("Enter your name to continue:")

if username:
    st.subheader(f"Welcome, {username.capitalize()}!")

    st.markdown("---")
    st.header("➕ Add New Transaction")

    t_type = st.selectbox("Type", ["Income", "Expense"])
    category = st.selectbox(
        "Category",
        ["Salary", "Food", "Travel", "Shopping", "Bills", "Health", "Other"]
    )
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    date = st.date_input("Date", datetime.now())
    desc = st.text_input("Description")

    if st.button("💾 Save Transaction"):
        new_data = pd.DataFrame([[t_type, category, amount, date, desc]], columns=expected_cols)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("Transaction saved successfully!")

    st.markdown("---")
    st.header("📊 Summary Overview")

    if not df.empty:
        try:
            total_income = df[df["Type"] == "Income"]["Amount"].sum()
            total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
            balance = total_income - total_expense

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"₹{total_income:,.2f}")
            col2.metric("Total Expense", f"₹{total_expense:,.2f}")
            col3.metric("Balance", f"₹{balance:,.2f}")

            # ---------- Visualization ----------
            st.markdown("### 💹 Expense Breakdown")
            expense_df = df[df["Type"] == "Expense"]
            if not expense_df.empty:
                fig, ax = plt.subplots()
                expense_df.groupby("Category")["Amount"].sum().plot(
                    kind="pie", autopct="%1.1f%%", ax=ax, startangle=90
                )
                ax.set_ylabel("")
                st.pyplot(fig)
            else:
                st.info("No expenses yet to visualize.")
        except Exception as e:
            st.error(f"⚠️ Error in summary: {e}")
    else:
        st.info("No transactions found. Add some to see the summary!")

    st.markdown("---")
    st.header("📜 Transaction History")

    if not df.empty:
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

        if st.button("🗑 Clear All Transactions"):
            os.remove(DATA_FILE)
            df = pd.DataFrame(columns=expected_cols)
            st.warning("All transactions deleted!")
            st.rerun()
    else:
        st.write("No records yet. Start by adding your first transaction!")

else:
    st.info("👆 Please enter your name to start tracking your expenses.")
