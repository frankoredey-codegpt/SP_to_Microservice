import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import mysql.connector
from decimal import Decimal

# Add the parent directory to sys.path to allow importing the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the lambda_handler directly from the correct path
from AWS_Lambda_Microservices.Fee_Calculation_Service import lambda_handler

class TestFeeCalculationService(unittest.TestCase):

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_premium_customer_no_fee(self, mock_connect):
        """Test that premium customers get no fee regardless of balance"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock account data for premium customer
        mock_cursor.fetchone.return_value = {
            'balance': Decimal('1000.00'),
            'customer_tier': 'premium'
        }

        event = {'account_id': 1}
        result = lambda_handler(event, None)

        self.assertEqual(result['account_id'], 1)
        self.assertEqual(result['calculated_fee'], 0.00)
        self.assertEqual(result['customer_tier'], 'premium')
        self.assertEqual(result['balance'], 1000.00)
        mock_cursor.close.assert_called()
        mock_conn.close.assert_called()

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_premium_customer_high_balance_no_fee(self, mock_connect):
        """Test that premium customers get no fee even with high balance"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('10000.00'),
            'customer_tier': 'premium'
        }

        event = {'account_id': 1}
        result = lambda_handler(event, None)

        self.assertEqual(result['calculated_fee'], 0.00)
        self.assertEqual(result['customer_tier'], 'premium')
        self.assertEqual(result['balance'], 10000.00)

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_high_balance_low_fee(self, mock_connect):
        """Test that non-premium customers with balance > 5000 get $5 fee"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('6000.00'),
            'customer_tier': 'gold'
        }

        event = {'account_id': 2}
        result = lambda_handler(event, None)

        self.assertEqual(result['account_id'], 2)
        self.assertEqual(result['calculated_fee'], 5.00)
        self.assertEqual(result['customer_tier'], 'gold')
        self.assertEqual(result['balance'], 6000.00)

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_exactly_5000_balance_low_fee(self, mock_connect):
        """Test that balance exactly at 5000 gets $15 fee (not > 5000)"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('5000.00'),
            'customer_tier': 'silver'
        }

        event = {'account_id': 3}
        result = lambda_handler(event, None)

        self.assertEqual(result['calculated_fee'], 15.00)
        self.assertEqual(result['balance'], 5000.00)

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_low_balance_high_fee(self, mock_connect):
        """Test that non-premium customers with balance <= 5000 get $15 fee"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('1500.00'),
            'customer_tier': 'bronze'
        }

        event = {'account_id': 4}
        result = lambda_handler(event, None)

        self.assertEqual(result['account_id'], 4)
        self.assertEqual(result['calculated_fee'], 15.00)
        self.assertEqual(result['customer_tier'], 'bronze')
        self.assertEqual(result['balance'], 1500.00)

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_zero_balance_high_fee(self, mock_connect):
        """Test that zero balance gets $15 fee"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('0.00'),
            'customer_tier': 'basic'
        }

        event = {'account_id': 5}
        result = lambda_handler(event, None)

        self.assertEqual(result['calculated_fee'], 15.00)
        self.assertEqual(result['balance'], 0.00)

    def test_missing_account_id(self):
        """Test error when account_id is missing"""
        event = {}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'account_id is required')

    def test_none_account_id(self):
        """Test error when account_id is None"""
        event = {'account_id': None}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'account_id is required')

    def test_empty_account_id(self):
        """Test error when account_id is empty string"""
        event = {'account_id': ''}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'account_id is required')

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_account_not_found(self, mock_connect):
        """Test error when account doesn't exist"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        event = {'account_id': 999}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Account not found')
        mock_cursor.close.assert_called()
        mock_conn.close.assert_called()

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_event_with_body_string(self, mock_connect):
        """Test handling event with JSON string body (API Gateway format)"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('3000.00'),
            'customer_tier': 'silver'
        }

        event = {
            'body': json.dumps({'account_id': 10})
        }
        result = lambda_handler(event, None)

        self.assertEqual(result['account_id'], 10)
        self.assertEqual(result['calculated_fee'], 15.00)

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_event_with_body_dict(self, mock_connect):
        """Test handling event with dictionary body"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('7500.00'),
            'customer_tier': 'gold'
        }

        event = {
            'body': {'account_id': 11}
        }
        result = lambda_handler(event, None)

        self.assertEqual(result['account_id'], 11)
        self.assertEqual(result['calculated_fee'], 5.00)

    def test_invalid_json_in_body(self):
        """Test error handling for invalid JSON in body"""
        event = {
            'body': '{invalid json}'
        }
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertIn('Internal server error', result['error'])

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_database_connection_error(self, mock_connect):
        """Test error handling for database connection failure"""
        mock_connect.side_effect = mysql.connector.Error("Connection failed")

        event = {'account_id': 1}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertIn('Internal server error', result['error'])

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_database_query_error(self, mock_connect):
        """Test error handling for database query failure"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = mysql.connector.Error("Query failed")

        event = {'account_id': 1}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertIn('Internal server error', result['error'])

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_decimal_balance_conversion(self, mock_connect):
        """Test that Decimal balance is properly converted to float"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('2500.75'),
            'customer_tier': 'standard'
        }

        event = {'account_id': 12}
        result = lambda_handler(event, None)

        self.assertEqual(result['balance'], 2500.75)
        self.assertIsInstance(result['balance'], float)
        self.assertEqual(result['calculated_fee'], 15.00)

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_case_sensitive_premium_tier(self, mock_connect):
        """Test that tier comparison is case sensitive"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Test with 'Premium' (capital P) - should not match 'premium'
        mock_cursor.fetchone.return_value = {
            'balance': Decimal('1000.00'),
            'customer_tier': 'Premium'
        }

        event = {'account_id': 13}
        result = lambda_handler(event, None)

        # Should get $15 fee because 'Premium' != 'premium' and balance <= 5000
        self.assertEqual(result['calculated_fee'], 15.00)
        self.assertEqual(result['customer_tier'], 'Premium')

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_boundary_value_5000_01(self, mock_connect):
        """Test boundary value just above 5000"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('5000.01'),
            'customer_tier': 'standard'
        }

        event = {'account_id': 14}
        result = lambda_handler(event, None)

        # Should get $5 fee because balance > 5000
        self.assertEqual(result['calculated_fee'], 5.00)
        self.assertEqual(result['balance'], 5000.01)

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_sql_injection_protection(self, mock_connect):
        """Test that parameterized queries protect against SQL injection"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        # Try to inject SQL
        event = {'account_id': "1; DROP TABLE Accounts; --"}
        result = lambda_handler(event, None)

        # Should safely handle the malicious input
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Account not found')
        
        # Verify the query was called with parameterized values
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        self.assertIn('%s', call_args[0][0])  # Verify parameterized query
        self.assertEqual(call_args[0][1], ("1; DROP TABLE Accounts; --",))  # Verify parameter

    @patch.dict(os.environ, {
        'DB_HOST': 'test-host',
        'DB_USER': 'test-user', 
        'DB_PASSWORD': 'test-pass',
        'DB_NAME': 'test-db'
    })
    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_environment_variables(self, mock_connect):
        """Test that environment variables are used for database connection"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('1000.00'),
            'customer_tier': 'premium'
        }

        event = {'account_id': 1}
        lambda_handler(event, None)

        # Verify connection was called with environment variables
        mock_connect.assert_called_once_with(
            host='test-host',
            user='test-user',
            password='test-pass',
            database='test-db',
            autocommit=True
        )

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_connection_cleanup_on_success(self, mock_connect):
        """Test that database connections are properly closed on success"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('1000.00'),
            'customer_tier': 'premium'
        }

        event = {'account_id': 1}
        lambda_handler(event, None)

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('AWS_Lambda_Microservices.Fee_Calculation_Service.mysql.connector.connect')
    def test_connection_cleanup_on_not_found(self, mock_connect):
        """Test that database connections are properly closed when account not found"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        event = {'account_id': 999}
        lambda_handler(event, None)

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
