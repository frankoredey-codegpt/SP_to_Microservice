import unittest
import json
import os
import mysql.connector
from unittest.mock import patch, MagicMock
from datetime import datetime
from decimal import Decimal

# Import only the lambda_handler since helper functions are nested inside it
from BankingRewardsFees_New.AWS_Lambda_Microservices.Account_Service import lambda_handler


class TestLambdaHandler(unittest.TestCase):
    
    @patch('mysql.connector.connect')
    def test_get_accounts(self, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_accounts = [
            {'account_id': 1, 'customer_name': 'John Doe', 'customer_id': 101},
            {'account_id': 2, 'customer_name': 'Jane Smith', 'customer_id': 102}
        ]
        mock_cursor.fetchall.return_value = mock_accounts
        
        event = {'action': 'get_accounts'}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once_with(dictionary=True)
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        self.assertEqual(result, mock_accounts)
    
    @patch('mysql.connector.connect')
    def test_get_account_details_success(self, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        account_id = 1
        mock_account = {
            'account_id': account_id,
            'customer_id': 101,
            'balance': Decimal('1000.50'),
            'created_at': datetime(2023, 1, 1, 12, 0, 0),
            'updated_at': datetime(2023, 1, 2, 12, 0, 0),
            'customer_name': 'John Doe',
            'customer_tier': 'Gold'
        }
        mock_cursor.fetchone.return_value = mock_account
        
        event = {'action': 'get_account_details', 'account_id': account_id}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once_with(dictionary=True)
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        
        expected_result = {
            'account_id': account_id,
            'customer_id': 101,
            'balance': 1000.5,
            'created_at': '2023-01-01 12:00:00',
            'updated_at': '2023-01-02 12:00:00',
            'customer_name': 'John Doe',
            'customer_tier': 'Gold'
        }
        self.assertEqual(result, expected_result)
    
    @patch('mysql.connector.connect')
    def test_get_account_details_not_found(self, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        account_id = 999  # Non-existent account
        mock_cursor.fetchone.return_value = None
        
        event = {'action': 'get_account_details', 'account_id': account_id}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertEqual(result, {'error': 'Account not found'})
    
    @patch('mysql.connector.connect')
    def test_update_balance_success(self, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.rowcount = 1
        
        account_id = 1
        new_balance = 2000.75
        event = {'action': 'update_balance', 'account_id': account_id, 'new_balance': new_balance}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        self.assertEqual(result, {'message': 'Balance updated successfully'})
    
    @patch('mysql.connector.connect')
    def test_update_balance_account_not_found(self, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.rowcount = 0
        
        account_id = 999  # Non-existent account
        new_balance = 2000.75
        event = {'action': 'update_balance', 'account_id': account_id, 'new_balance': new_balance}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertEqual(result, {'error': 'Account not found'})
    
    def test_invalid_action(self):
        # Arrange
        event = {'action': 'invalid_action'}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertEqual(result, {'error': 'Invalid action: invalid_action. Available actions: get_accounts, get_account_details, update_balance'})
    
    @patch('mysql.connector.connect')
    def test_missing_account_id_for_get_account_details(self, mock_connect):
        # Arrange
        event = {'action': 'get_account_details'}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertEqual(result, {'error': 'account_id is required'})
        mock_connect.assert_not_called()
    
    @patch('mysql.connector.connect')
    def test_missing_parameters_for_update_balance(self, mock_connect):
        # Arrange
        event = {'action': 'update_balance', 'account_id': 1}  # Missing new_balance
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertEqual(result, {'error': 'account_id and new_balance are required'})
        mock_connect.assert_not_called()
    
    @patch('mysql.connector.connect')
    def test_missing_new_balance_for_update_balance(self, mock_connect):
        # Arrange
        event = {'action': 'update_balance', 'new_balance': 1000.0}  # Missing account_id
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertEqual(result, {'error': 'account_id and new_balance are required'})
        mock_connect.assert_not_called()
    
    @patch('mysql.connector.connect')
    def test_database_error(self, mock_connect):
        # Arrange
        mock_connect.side_effect = mysql.connector.Error("Database connection error")
        event = {'action': 'get_accounts'}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertTrue('error' in result)
        self.assertTrue('Database error' in result['error'])
    
    @patch('mysql.connector.connect')
    def test_general_exception(self, mock_connect):
        # Arrange
        mock_connect.side_effect = Exception("Unexpected error")
        event = {'action': 'get_accounts'}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertTrue('error' in result)
        self.assertTrue('Internal server error' in result['error'])
    
    def test_json_string_body(self):
        # Arrange
        event = {
            'body': json.dumps({'action': 'get_accounts'})
        }
        
        with patch('mysql.connector.connect') as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = []
            
            # Act
            result = lambda_handler(event, None)
            
            # Assert
            mock_connect.assert_called_once()
            mock_conn.cursor.assert_called_once_with(dictionary=True)
            self.assertEqual(result, [])
    
    def test_json_decode_error(self):
        # Arrange
        event = {
            'body': '{"action": "get_accounts", invalid_json}'  # Invalid JSON
        }
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertTrue('error' in result)
        self.assertTrue('JSON decode error' in result['error'])
    
    @patch('mysql.connector.connect')
    def test_datetime_serialization_in_get_accounts(self, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_accounts = [
            {
                'account_id': 1, 
                'customer_name': 'John Doe', 
                'customer_id': 101,
                'created_at': datetime(2023, 1, 1, 12, 0, 0),
                'balance': Decimal('1000.50')
            }
        ]
        mock_cursor.fetchall.return_value = mock_accounts
        
        event = {'action': 'get_accounts'}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        expected_result = [
            {
                'account_id': 1, 
                'customer_name': 'John Doe', 
                'customer_id': 101,
                'created_at': '2023-01-01 12:00:00',
                'balance': 1000.5
            }
        ]
        self.assertEqual(result, expected_result)
    
    @patch('mysql.connector.connect')
    def test_update_balance_with_zero_balance(self, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.rowcount = 1
        
        account_id = 1
        new_balance = 0.0  # Test with zero balance
        event = {'action': 'update_balance', 'account_id': account_id, 'new_balance': new_balance}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertEqual(result, {'message': 'Balance updated successfully'})
    
    @patch('mysql.connector.connect')
    def test_update_balance_with_negative_balance(self, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.rowcount = 1
        
        account_id = 1
        new_balance = -100.0  # Test with negative balance
        event = {'action': 'update_balance', 'account_id': account_id, 'new_balance': new_balance}
        
        # Act
        result = lambda_handler(event, None)
        
        # Assert
        self.assertEqual(result, {'message': 'Balance updated successfully'})


if __name__ == '__main__':
    unittest.main()
