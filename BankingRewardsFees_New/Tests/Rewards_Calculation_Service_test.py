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
from AWS_Lambda_Microservices.Rewards_Calculation_Service import lambda_handler

class TestRewardsCalculationService(unittest.TestCase):

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_high_balance_high_reward(self, mock_connect):
        """Test that balance > $10,000 gets 2% reward"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock account data with high balance
        mock_cursor.fetchone.return_value = {
            'balance': Decimal('15000.00')
        }

        event = {'account_id': 1}
        result = lambda_handler(event, None)

        expected_reward = 15000.00 * 0.02  # 2% = 300.00
        self.assertEqual(result['account_id'], 1)
        self.assertEqual(result['calculated_reward'], 300.00)
        self.assertEqual(result['balance'], 15000.00)
        mock_cursor.close.assert_called()
        mock_conn.close.assert_called()

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_low_balance_low_reward(self, mock_connect):
        """Test that balance <= $10,000 gets 1% reward"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock account data with low balance
        mock_cursor.fetchone.return_value = {
            'balance': Decimal('5000.00')
        }

        event = {'account_id': 2}
        result = lambda_handler(event, None)

        expected_reward = 5000.00 * 0.01  # 1% = 50.00
        self.assertEqual(result['account_id'], 2)
        self.assertEqual(result['calculated_reward'], 50.00)
        self.assertEqual(result['balance'], 5000.00)

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_exactly_10000_balance_low_reward(self, mock_connect):
        """Test that balance exactly at $10,000 gets 1% reward (not > 10000)"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('10000.00')
        }

        event = {'account_id': 3}
        result = lambda_handler(event, None)

        expected_reward = 10000.00 * 0.01  # 1% = 100.00
        self.assertEqual(result['calculated_reward'], 100.00)
        self.assertEqual(result['balance'], 10000.00)

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_boundary_value_10000_01(self, mock_connect):
        """Test boundary value just above $10,000"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('10000.01')
        }

        event = {'account_id': 4}
        result = lambda_handler(event, None)

        expected_reward = 10000.01 * 0.02  # 2% = 200.0002, rounded to 200.00
        self.assertEqual(result['calculated_reward'], 200.00)
        self.assertEqual(result['balance'], 10000.01)

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_zero_balance_zero_reward(self, mock_connect):
        """Test that zero balance gets zero reward"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('0.00')
        }

        event = {'account_id': 5}
        result = lambda_handler(event, None)

        self.assertEqual(result['calculated_reward'], 0.00)
        self.assertEqual(result['balance'], 0.00)

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_small_balance_reward_rounding(self, mock_connect):
        """Test reward calculation and rounding for small balances"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('123.45')
        }

        event = {'account_id': 6}
        result = lambda_handler(event, None)

        expected_reward = 123.45 * 0.01  # 1% = 1.2345, rounded to 1.23
        self.assertEqual(result['calculated_reward'], 1.23)
        self.assertEqual(result['balance'], 123.45)

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_large_balance_reward_rounding(self, mock_connect):
        """Test reward calculation and rounding for large balances"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('25678.99')
        }

        event = {'account_id': 7}
        result = lambda_handler(event, None)

        expected_reward = 25678.99 * 0.02  # 2% = 513.5798, rounded to 513.58
        self.assertEqual(result['calculated_reward'], 513.58)
        self.assertEqual(result['balance'], 25678.99)

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

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
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

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_event_with_body_string(self, mock_connect):
        """Test handling event with JSON string body (API Gateway format)"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('8000.00')
        }

        event = {
            'body': json.dumps({'account_id': 10})
        }
        result = lambda_handler(event, None)

        expected_reward = 8000.00 * 0.01  # 1% = 80.00
        self.assertEqual(result['account_id'], 10)
        self.assertEqual(result['calculated_reward'], 80.00)

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_event_with_body_dict(self, mock_connect):
        """Test handling event with dictionary body"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('12000.00')
        }

        event = {
            'body': {'account_id': 11}
        }
        result = lambda_handler(event, None)

        expected_reward = 12000.00 * 0.02  # 2% = 240.00
        self.assertEqual(result['account_id'], 11)
        self.assertEqual(result['calculated_reward'], 240.00)

    def test_invalid_json_in_body(self):
        """Test error handling for invalid JSON in body"""
        event = {
            'body': '{invalid json}'
        }
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertIn('Internal server error', result['error'])

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_database_connection_error(self, mock_connect):
        """Test error handling for database connection failure"""
        mock_connect.side_effect = mysql.connector.Error("Connection failed")

        event = {'account_id': 1}
        result = lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertIn('Internal server error', result['error'])

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
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

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_decimal_balance_conversion(self, mock_connect):
        """Test that Decimal balance is properly converted to float"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('7500.75')
        }

        event = {'account_id': 12}
        result = lambda_handler(event, None)

        self.assertEqual(result['balance'], 7500.75)
        self.assertIsInstance(result['balance'], float)
        expected_reward = 7500.75 * 0.01  # 1% = 75.0075, rounded to 75.01
        self.assertEqual(result['calculated_reward'], 75.01)

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
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
    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_environment_variables(self, mock_connect):
        """Test that environment variables are used for database connection"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('5000.00')
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

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_connection_cleanup_on_success(self, mock_connect):
        """Test that database connections are properly closed on success"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('5000.00')
        }

        event = {'account_id': 1}
        lambda_handler(event, None)

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
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

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_reward_calculation_precision(self, mock_connect):
        """Test reward calculation precision with various decimal places"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        test_cases = [
            # (balance, expected_reward)
            (Decimal('1000.33'), 10.00),  # 1000.33 * 0.01 = 10.0033 -> 10.00
            (Decimal('1000.37'), 10.00),  # 1000.37 * 0.01 = 10.0037 -> 10.00
            (Decimal('1000.39'), 10.00),  # 1000.39 * 0.01 = 10.0039 -> 10.00
            (Decimal('15000.55'), 300.01), # 15000.55 * 0.02 = 300.011 -> 300.01
            (Decimal('15000.54'), 300.01), # 15000.54 * 0.02 = 300.0108 -> 300.01
        ]

        for balance, expected_reward in test_cases:
            with self.subTest(balance=balance):
                mock_cursor.fetchone.return_value = {'balance': balance}
                
                event = {'account_id': 1}
                result = lambda_handler(event, None)
                
                self.assertEqual(result['calculated_reward'], expected_reward)

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_negative_balance_handling(self, mock_connect):
        """Test handling of negative balance (edge case)"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('-500.00')
        }

        event = {'account_id': 13}
        result = lambda_handler(event, None)

        # Negative balance should get 1% (since -500 is not > 10000)
        expected_reward = -500.00 * 0.01  # -5.00
        self.assertEqual(result['calculated_reward'], -5.00)
        self.assertEqual(result['balance'], -500.00)

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_very_large_balance(self, mock_connect):
        """Test handling of very large balance"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('1000000.00')  # 1 million
        }

        event = {'account_id': 14}
        result = lambda_handler(event, None)

        expected_reward = 1000000.00 * 0.02  # 2% = 20000.00
        self.assertEqual(result['calculated_reward'], 20000.00)
        self.assertEqual(result['balance'], 1000000.00)

    @patch('AWS_Lambda_Microservices.Rewards_Calculation_Service.mysql.connector.connect')
    def test_fractional_cents_balance(self, mock_connect):
        """Test handling of balance with fractional cents"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'balance': Decimal('1000.999')  # More than 2 decimal places
        }

        event = {'account_id': 15}
        result = lambda_handler(event, None)

        expected_reward = 1000.999 * 0.01  # 1% = 10.00999, rounded to 10.01
        self.assertEqual(result['calculated_reward'], 10.01)
        self.assertEqual(result['balance'], 1000.999)

if __name__ == '__main__':
    unittest.main()
