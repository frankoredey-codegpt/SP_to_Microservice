# File: BankingRewardsFees_Old/app.py
import streamlit as st
import mysql.connector
import pandas as pd

# ---- DB connection ----
def get_connection():
    return mysql.connector.connect(
        host="database-2.crq7shsasjo0.us-west-2.rds.amazonaws.com", # <<< REPLACE WITH YOUR ACTUAL MYSQL HOST
        user="admin",
        password="demo1234!",
        database="BankingRewardsFees_Old"
    )

# ---- Get account list ----
def get_accounts():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT account_id, customer_name FROM Accounts")
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return accounts

# ---- Get account details ----
def get_account_details(account_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Accounts WHERE account_id = %s", (account_id,))
    account = cursor.fetchone()
    cursor.close()
    conn.close()
    return account

# ---- Call stored procedure to calculate fees ----
def calculate_fees(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("CalculateMonthlyFees", [account_id])
    conn.commit()
    cursor.close()
    conn.close()

# ---- Call stored procedure to calculate rewards ----
def calculate_rewards(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("CalculateRewards", [account_id])
    conn.commit()
    cursor.close()
    conn.close()

# ---- Update account balance ----
def update_account_balance(account_id, new_balance):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Accounts SET balance = %s WHERE account_id = %s", (new_balance, account_id))
    conn.commit()
    cursor.close()
    conn.close()

# ---- Streamlit UI ----
st.title("Banking Rewards & Fees Demo (Legacy SP Version)")

accounts = get_accounts()
account_options = {f"{a['customer_name']} (ID: {a['account_id']})": a['account_id'] for a in accounts}

selected_account_label = st.selectbox("Select an Account", options=list(account_options.keys()))
selected_account_id = account_options[selected_account_label]

if st.button("Calculate Fees"):
    calculate_fees(selected_account_id)
    st.success("Fees calculated and updated!")

if st.button("Calculate Rewards"):
    calculate_rewards(selected_account_id)
    st.success("Rewards calculated and updated!")

# Display current account data
account_details = get_account_details(selected_account_id)
if account_details:
    st.subheader("Account Details (After Updates)")

    # Make balance editable
    current_balance = float(account_details.get('balance', 0.0))
    new_balance = st.number_input("Balance", value=current_balance, format="%.2f")

    if st.button("Save Balance"):
        update_account_balance(selected_account_id, new_balance)
        st.success(f"Balance updated to {new_balance:.2f}!")
        # Re-fetch account details to display the updated value
        account_details = get_account_details(selected_account_id)

    # Display other account details
    display_df = pd.DataFrame([account_details])
    # Remove 'balance' from this display as it's handled by number_input
    if 'balance' in display_df.columns:
        display_df = display_df.drop(columns=['balance'])
    st.write(display_df)
