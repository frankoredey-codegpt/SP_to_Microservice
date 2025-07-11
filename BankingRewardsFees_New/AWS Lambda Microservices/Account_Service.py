# account_service.py - Fixed Version with Datetime Handling
import json
import mysql.connector
import os
from decimal import Decimal
from datetime import datetime
import traceback

def lambda_handler(event, context):
    """
    Account Service Lambda Function - Fixed Version
    """
    
    def get_connection():
        return mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'database-2.crq7shsasjo0.us-west-2.rds.amazonaws.com'),
            user=os.environ.get('DB_USER', 'admin'),
            password=os.environ.get('DB_PASSWORD', 'demo1234!'),
            database=os.environ.get('DB_NAME', 'BankingRewardsFees_New'),
            autocommit=True
        )
    
    def serialize_datetime(obj):
        """Convert datetime and decimal objects to JSON serializable format"""
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj
    
    def convert_account_data(account_dict):
        """Convert all datetime and decimal fields in account data"""
        if account_dict:
            converted = {}
            for key, value in account_dict.items():
                converted[key] = serialize_datetime(value)
            return converted
        return account_dict
    
    try:
        # Parse the event data
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        action = body.get('action')
        
        if action == 'get_accounts':
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT a.account_id, c.name as customer_name, c.customer_id
                FROM Accounts a 
                JOIN Customers c ON a.customer_id = c.customer_id
                ORDER BY a.account_id
            """)
            accounts = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Convert any datetime/decimal fields
            converted_accounts = []
            for account in accounts:
                converted_accounts.append(convert_account_data(account))
            
            return converted_accounts
            
        elif action == 'get_account_details':
            account_id = body.get('account_id')
            
            if not account_id:
                return {'error': 'account_id is required'}
            
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    a.account_id,
                    a.customer_id,
                    a.balance,
                    a.created_at,
                    a.updated_at,
                    c.name as customer_name, 
                    c.tier as customer_tier
                FROM Accounts a 
                JOIN Customers c ON a.customer_id = c.customer_id
                WHERE a.account_id = %s
            """, (account_id,))
            
            account = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not account:
                return {'error': 'Account not found'}
            
            # Convert datetime and decimal fields
            return convert_account_data(account)
            
        elif action == 'update_balance':
            account_id = body.get('account_id')
            new_balance = body.get('new_balance')
            
            if not account_id or new_balance is None:
                return {'error': 'account_id and new_balance are required'}
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Accounts 
                SET balance = %s, updated_at = NOW() 
                WHERE account_id = %s
            """, (new_balance, account_id))
            
            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return {'error': 'Account not found'}
            
            cursor.close()
            conn.close()
            
            return {'message': 'Balance updated successfully'}
            
        else:
            return {'error': f'Invalid action: {action}. Available actions: get_accounts, get_account_details, update_balance'}
            
    except mysql.connector.Error as e:
        error_msg = f'Database error: {str(e)}'
        print(f"Database error: {e}")
        return {'error': error_msg}
    except json.JSONDecodeError as e:
        error_msg = f'JSON decode error: {str(e)}'
        print(f"JSON decode error: {e}")
        return {'error': error_msg}
    except Exception as e:
        error_msg = f'Internal server error: {str(e)}'
        print(f"Unexpected error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {'error': error_msg}
