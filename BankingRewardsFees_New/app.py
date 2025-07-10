# BankingRewardsFees_New/app.py - Production Version
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
            # Handle different response formats
            response_data = response.json()
            
            # If it's a direct array/object (like your current setup)
            if isinstance(response_data, list) or (isinstance(response_data, dict) and 'body' not in response_data):
                return response_data
            
            # If it's AWS Lambda format with 'body' key
            if isinstance(response_data, dict) and 'body' in response_data:
                if isinstance(response_data['body'], str):
                    return json.loads(response_data['body'])
                else:
                    return response_data['body']
            
            return response_data
        else:
            st.error(f"Account service error: {response.status_code} - {response.text}")
            return None
    except json.JSONDecodeError as e:
        st.error(f"JSON decode error: {str(e)}")
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
            response_data = response.json()
            
            # Handle different response formats
            if isinstance(response_data, dict) and 'body' in response_data:
                if isinstance(response_data['body'], str):
                    return json.loads(response_data['body'])
                else:
                    return response_data['body']
            else:
                return response_data
        else:
            st.error(f"Fee calculation service error: {response.status_code} - {response.text}")
            return None
    except json.JSONDecodeError as e:
        st.error(f"JSON decode error: {str(e)}")
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
            response_data = response.json()
            
            # Handle different response formats
            if isinstance(response_data, dict) and 'body' in response_data:
                if isinstance(response_data['body'], str):
                    return json.loads(response_data['body'])
                else:
                    return response_data['body']
            else:
                return response_data
        else:
            st.error(f"Rewards calculation service error: {response.status_code} - {response.text}")
            return None
    except json.JSONDecodeError as e:
        st.error(f"JSON decode error: {str(e)}")
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
    # Handle case where accounts might be a list or dict
    if isinstance(accounts, list) and len(accounts) > 0:
        account_options = {f"{a.get('customer_name', 'Unknown')} (ID: {a.get('account_id', 'N/A')})": a.get('account_id') for a in accounts if a.get('account_id')}
        
        if account_options:
            selected_account_label = st.selectbox("Select an Account", options=list(account_options.keys()))
            selected_account_id = account_options[selected_account_label]
            
            # Action buttons in columns
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Calculate Fees"):
                    fee_result = call_fee_calculation_service(selected_account_id)
                    if fee_result:
                        st.session_state.calculated_fee = fee_result
                        st.success(f"Monthly fee calculated: ${fee_result.get('calculated_fee', 0):.2f}")
            
            with col2:
                if st.button("Calculate Rewards"):
                    reward_result = call_rewards_calculation_service(selected_account_id)
                    if reward_result:
                        st.session_state.calculated_reward = reward_result
                        st.success(f"Monthly reward calculated: ${reward_result.get('calculated_reward', 0):.2f}")
            
            # Display calculated values
            if st.session_state.calculated_fee:
                fee_data = st.session_state.calculated_fee
                st.info(f"**Latest Fee Calculation:** ${fee_data.get('calculated_fee', 0):.2f} "
                        f"(Tier: {fee_data.get('customer_tier', 'N/A')}, "
                        f"Balance: ${fee_data.get('balance', 0):.2f})")
            
            if st.session_state.calculated_reward:
                reward_data = st.session_state.calculated_reward
                st.info(f"**Latest Reward Calculation:** ${reward_data.get('calculated_reward', 0):.2f} "
                        f"(Balance: ${reward_data.get('balance', 0):.2f})")
            
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
                        st.rerun()
                
                # Display other account details
                display_data = {
                    'Account ID': account_details.get('account_id'),
                    'Customer Name': account_details.get('customer_name'),
                    'Customer Tier': account_details.get('customer_tier'),
                    'Customer ID': account_details.get('customer_id'),
                    'Balance': f"${account_details.get('balance', 0):.2f}",
                    'Created At': account_details.get('created_at'),
                    'Updated At': account_details.get('updated_at')
                }
                
                display_df = pd.DataFrame([display_data])
                st.write(display_df)
            else:
                st.warning("Could not load account details. Please check the Account Service.")
        else:
            st.error("No valid accounts found in the response.")
    else:
        st.error("Invalid accounts data format received from service.")
else:
    st.error("Unable to load accounts. Please check the Account Service.")

# Add footer with architecture info
st.markdown("---")
st.markdown("**Architecture:** Microservices with AWS Lambda Functions")
st.markdown("- **Account Service:** Manages account data and balance updates")
st.markdown("- **Fee Calculation Service:** Calculates monthly fees based on tier and balance")
st.markdown("- **Rewards Calculation Service:** Calculates rewards based on balance")
