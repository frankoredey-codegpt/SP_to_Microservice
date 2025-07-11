# fee_calculation_service.py - Consistent Response Format
import json
import mysql.connector
import os
from decimal import Decimal
import traceback

def lambda_handler(event, context):
    """
    Fee Calculation Service Lambda Function
    """
    
    def get_connection():
        return mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'database-2.crq7shsasjo0.us-west-2.rds.amazonaws.com'),
            user=os.environ.get('DB_USER', 'admin'),
            password=os.environ.get('DB_PASSWORD', 'demo1234!'),
            database=os.environ.get('DB_NAME', 'BankingRewardsFees_New'),
            autocommit=True
        )
    
    try:
        # Parse the event data
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        account_id = body.get('account_id')
        if not account_id:
            return {'error': 'account_id is required'}
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT a.balance, c.tier as customer_tier
            FROM Accounts a 
            JOIN Customers c ON a.customer_id = c.customer_id
            WHERE a.account_id = %s
        """, (account_id,))
        
        account = cursor.fetchone()
        if not account:
            cursor.close()
            conn.close()
            return {'error': 'Account not found'}
        
        # Business logic
        customer_tier = account['customer_tier']
        balance = float(account['balance'])
        
        if customer_tier == 'premium':
            fee = 0.00
        elif balance > 5000:
            fee = 5.00
        else:
            fee = 15.00
        
        cursor.close()
        conn.close()
        
        return {
            'account_id': account_id,
            'calculated_fee': fee,
            'customer_tier': customer_tier,
            'balance': balance
        }
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {'error': f'Internal server error: {str(e)}'}
