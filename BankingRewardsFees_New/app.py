# BankingRewardsFees_New/app.py
import streamlit as st
import requests
import json
import pandas as pd

# AWS Lambda Function URLs - REPLACE WITH YOUR ACTUAL LAMBDA FUNCTION URLs
ACCOUNT_SERVICE_URL = "https://h4s7q404t9.execute-api.us-west-2.amazonaws.com/default/Account_Service"
FEE_CALCULATION_URL = "https://31ex1bcgtg.execute-api.us-west-2.amazonaws.com/default/Fee_Calculation_Service"
REWARDS_CALCULATION_URL = "https://we5fvnijya.execute-api.us-west-2.amazonaws.com/default/Rewards_Calculation_Service"

# ---- Lambda Service Calls ----
def call_account_service(action, **kwargs):
    """Call the Account Service Lambda function"""
    payload = {"action": action, **kwargs}
    try:
        response = requests.post(ACCOUNT_SERVICE_URL, json=payload)
        if response.status_code == 200:
            return json.loads(response.json()['body'])
        else:
            st.error(f"Account service error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error calling account service: {str(e)}")
        return None

def call_fee_calculation_service(account_id):
    """Call the Fee Calculation Service Lambda function"""
    payload = {"account_id": account_id}
    try:
        response = requests.post(FEE_CALCULATION_URL, json=payload)
        if response.status_code == 200:
            return json.loads(response.json()['body'])
        else:
            st.error(f"Fee calculation service error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error calling fee calculation service: {str(e)}")
        return None

def call_rewards_calculation_service(account_id):
    """Call the Rewards Calculation Service Lambda function"""
    payload = {"account_id": account_id}
    try:
        response = requests.post(REWARDS_CALCULATION_URL, json=payload)
        if response.status_code == 200:
            return json.loads(response.json()['body'])
        else:
            st.error(f"Rewards calculation service error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error calling rewards calculation service: {str(e)}")
        return None

# ---- Helper Functions ----
def get_accounts():
    """Get list of accounts from Account Service"""
    return call_account_service("get_accounts")

def get_account_details(account_id):
    """Get account details from Account Service"""
    return call_account_service("get_account_details", account_id=account_id)

def update_account_balance(account_id, new_balance):
    """Update account balance via Account Service"""
    return call_account_service("update_balance", account_id=account_id, new_balance=new_balance)

# ---- Streamlit UI ----
st.title("Banking Rewards & Fees Demo (Microservices Version)")

# Initialize session state for calculated values
if 'calculated_fee' not in st.session_state:
    st.session_state.calculated_fee = None
if 'calculated_reward' not in st.session_state:
    st.session_state.calculated_reward = None

accounts = get_accounts()
if accounts:
    account_options = {f"{a['customer_name']} (ID: {a['account_id']})": a['account_id'] for a in accounts}
    
    selected_account_label = st.selectbox("Select an Account", options=list(account_options.keys()))
    selected_account_id = account_options[selected_account_label]
    
    # Action buttons in columns
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Calculate Fees"):
            fee_result = call_fee_calculation_service(selected_account_id)
            if fee_result:
                st.session_state.calculated_fee = fee_result
                st.success(f"Monthly fee calculated: ${fee_result['calculated_fee']:.2f}")
    
    with col2:
        if st.button("Calculate Rewards"):
            reward_result = call_rewards_calculation_service(selected_account_id)
            if reward_result:
                st.session_state.calculated_reward = reward_result
                st.success(f"Monthly reward calculated: ${reward_result['calculated_reward']:.2f}")
    
    # Display calculated values
    if st.session_state.calculated_fee:
        st.info(f"**Latest Fee Calculation:** ${st.session_state.calculated_fee['calculated_fee']:.2f} "
                f"(Tier: {st.session_state.calculated_fee['customer_tier']}, "
                f"Balance: ${st.session_state.calculated_fee['balance']:.2f})")
    
    if st.session_state.calculated_reward:
        st.info(f"**Latest Reward Calculation:** ${st.session_state.calculated_reward['calculated_reward']:.2f} "
                f"(Balance: ${st.session_state.calculated_reward['balance']:.2f})")
    
    # Display current account data
    account_details = get_account_details(selected_account_id)
    if account_details:
        st.subheader("Account Details")
        
        # Make balance editable
        current_balance = float(account_details.get('balance', 0.0))
        new_balance = st.number_input("Balance", value=current_balance, format="%.2f")
        
        if st.button("Save Balance"):
            result = update_account_balance(selected_account_id, new_balance)
            if result:
                st.success(f"Balance updated to ${new_balance:.2f}!")
                # Clear calculated values since balance changed
                st.session_state.calculated_fee = None
                st.session_state.calculated_reward = None
                # Re-fetch account details
                account_details = get_account_details(selected_account_id)
        
        # Display other account details
        display_data = {
            'Account ID': account_details.get('account_id'),
            'Customer Name': account_details.get('customer_name'),
            'Customer Tier': account_details.get('customer_tier'),
            'Customer ID': account_details.get('customer_id'),
            'Created At': account_details.get('created_at'),
            'Updated At': account_details.get('updated_at')
        }
        
        display_df = pd.DataFrame([display_data])
        st.write(display_df)
else:
    st.error("Unable to load accounts. Please check the Account Service.")
