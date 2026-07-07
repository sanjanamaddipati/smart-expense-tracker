import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import date

# ---------- Database Setup ----------
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    description TEXT,
    amount REAL
)
""")
conn.commit()

# ---------- Page Config ----------
st.set_page_config(page_title="Smart Expense Tracker", layout="wide")
st.title("💰 Smart Expense Tracker")

# ---------- Add Expense Form ----------
st.subheader("Add New Expense")

with st.form("expense_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        exp_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Other"])
    with col2:
        description = st.text_input("Description")
        amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)

    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if amount > 0:
            cursor.execute(
                "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
                (str(exp_date), category, description, amount)
            )
            conn.commit()
            st.success("Expense added successfully!")
        else:
            st.error("Amount should be greater than 0")

# ---------- Load Data ----------
df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)

st.subheader("All Expenses")

if not df.empty:
    st.dataframe(df, use_container_width=True)

    total = df["amount"].sum()
    st.metric("Total Spent", f"₹{total:,.2f}")

    # ---------- Filter ----------
    st.subheader("Filter by Category")
    selected_cat = st.multiselect("Select Category", options=df["category"].unique(), default=df["category"].unique())
    filtered_df = df[df["category"].isin(selected_cat)]

    # ---------- Charts ----------
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Category-wise Spending")
        cat_sum = filtered_df.groupby("category")["amount"].sum()
        fig1, ax1 = plt.subplots()
        ax1.pie(cat_sum, labels=cat_sum.index, autopct="%1.1f%%")
        ax1.axis("equal")
        st.pyplot(fig1)

    with col2:
        st.write("### Daily Spending Trend")
        daily_sum = filtered_df.groupby("date")["amount"].sum()
        fig2, ax2 = plt.subplots()
        daily_sum.plot(kind="bar", ax=ax2, color="skyblue")
        ax2.set_ylabel("Amount (₹)")
        st.pyplot(fig2)

    # ---------- Delete Option ----------
    st.subheader("Delete an Expense")
    delete_id = st.number_input("Enter ID to delete", min_value=0, step=1)
    if st.button("Delete"):
        cursor.execute("DELETE FROM expenses WHERE id = ?", (delete_id,))
        conn.commit()
        st.success(f"Expense with ID {delete_id} deleted. Please refresh.")
else:
    st.info("No expenses added yet. Add your first expense above!")