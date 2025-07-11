import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import mysql.connector
from datetime import datetime
from decimal import Decimal

# Add the parent directory to sys.path to allow importing the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the lambda_handler directly from the correct path
from AWS_Lambda_Microservices.Account_Service import lambda_handler

class TestAccountService(unittest.TestCase):

    @patch('AWS_Lambda_Microservices.Account_Service.mysql.connector.connect')
    def test_get_accounts(self, mock_connect):
        # Mock cursor and connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetchall result
        mock_cursor.fetchall.return_value = [
            {'account_id': 1, 'customer_name': 'John Doe', 'customer_id': 100},
            {'account_id': 2, 'customer_name': 'Jane Doe', 'customer_id': 101}
        ]

        # Test with direct event structure (no body wrapper)
        event = {'action': 'get_accounts'}
        result = lambda_handler(event, None)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['customer_name'], 'John Doe')
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called()
        mock_conn.close.assert_called()

    @patch('AWS_Lambda_Microservices.Account_Service.mysql.connector.connect')
    def test_get_accounts_with_body(self, mock_connect):
        # Mock cursor and connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetchall result
        mock_cursor.fetchall.return_value = [
            {'account_id': 1, 'customer_name': 'John Doe', 'customer_id': 100}
        ]

        # Test with body wrapper (API Gateway style)
        event = {
            'body': json.dumps({'action': 'get_accounts'})
        }
        result = lambda_handler(event, None)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['customer_name'], 'John Doe')

    @patch('AWS_Lambda_Microservices.Account_Service.mysql.connector.connect')
    def test_get_account_details_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetchone result with datetime and decimal values
        mock_cursor.fetchone.return_value = {
            'account_id': 1,
            'customer_id': 100,
            'balance': Decimal('500.50'),
            'created_at': datetime(2023, 1, 1, 12, 0, 0),
            'updated_at': datetime(2023, 1, 2, 12, 0, 0),
            'customer_name': 'John Doe',
            'customer_tier': 'Gold'
        }

        event = {'action': 'get_account_details', 'account_id': 1}
        result = lambda_handler(event, None)

        self.assertIn('account_id', result)
        self.assertEqual(result['customer_name'], 'John Doe')
        self.assertEqual(result['balance'], 500.5)  # Should be converted to float
        self.assertEqual(result['created_at'], '2023-01-01 12:00:00')  # Should be converted to string
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called()
        mock_conn.close.assert_called()

    def test_get_account_details_missing_id(self):
        event = {'action': 'get_account_details'}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'account_id is required')

    @patch('AWS_Lambda_Microservices.Account_Service.mysql.connector.connect')
    def test_get_account_details_not_found(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        event = {'action': 'get_account_details', 'account_id': 999}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Account not found')
        mock_cursor.close.assert_called()
        mock_conn.close.assert_called()

    @patch('AWS_Lambda_Microservices.Account_Service.mysql.connector.connect')
    def test_update_balance_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.rowcount = 1

        event = {'action': 'update_balance', 'account_id': 1, 'new_balance': 1000.0}
        result = lambda_handler(event, None)

        self.assertIn('message', result)
        self.assertEqual(result['message'], 'Balance updated successfully')
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called()
        mock_conn.close.assert_called()

    def test_update_balance_missing_fields(self):
        # Test missing account_id
        event = {'action': 'update_balance', 'new_balance': 1000.0}
        result = lambda_handler(event, None)
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'account_id and new_balance are required')

        # Test missing new_balance
        event = {'action': 'update_balance', 'account_id': 1}
        result = lambda_handler(event, None)
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'account_id and new_balance are required')

        # Test new_balance is None (explicitly)
        event = {'action': 'update_balance', 'account_id': 1, 'new_balance': None}
        result = lambda_handler(event, None)
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'account_id and new_balance are required')

    @patch('AWS_Lambda_Microservices.Account_Service.mysql.connector.connect')
    def test_update_balance_account_not_found(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.rowcount = 0

        event = {'action': 'update_balance', 'account_id': 999, 'new_balance': 1000.0}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Account not found')
        mock_cursor.close.assert_called()
        mock_conn.close.assert_called()

    def test_invalid_action(self):
        event = {'action': 'non_existing_action'}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertTrue('Invalid action' in result['error'])

    @patch('AWS_Lambda_Microservices.Account_Service.mysql.connector.connect')
    def test_database_error(self, mock_connect):
        # Setup mock to raise a database error
        mock_connect.side_effect = mysql.connector.Error("Test database error")

        event = {'action': 'get_accounts'}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Database error: Test database error')

    def test_json_decode_error(self):
        # Test with invalid JSON in body
        event = {'body': '{invalid json}'}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertTrue('JSON decode error' in result['error'])

    def test_update_balance_with_zero(self):
        # Test that zero balance is allowed (not treated as None/missing)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        with patch('AWS_Lambda_Microservices.Account_Service.mysql.connector.connect', return_value=mock_conn):
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.rowcount = 1

            event = {'action': 'update_balance', 'account_id': 1, 'new_balance': 0.0}
            result = lambda_handler(event, None)

            self.assertIn('message', result)
            self.assertEqual(result['message'], 'Balance updated successfully')

    @patch('AWS_Lambda_Microservices.Account_Service.mysql.connector.connect')
    def test_datetime_decimal_serialization(self, mock_connect):
        """Test that datetime and decimal objects are properly serialized"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock data with various types that need serialization
        mock_cursor.fetchall.return_value = [
            {
                'account_id': 1, 
                'customer_name': 'John Doe', 
                'customer_id': 100,
                'balance': Decimal('1500.75'),
                'created_at': datetime(2023, 5, 15, 14, 30, 45)
            }
        ]

        event = {'action': 'get_accounts'}
        result = lambda_handler(event, None)

        # Verify serialization worked correctly
        self.assertEqual(result[0]['balance'], 1500.75)
        self.assertEqual(result[0]['created_at'], '2023-05-15 14:30:45')

if __name__ == '__main__':
    unittest.main()
