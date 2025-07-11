import unittest
import json
import os
import mysql.connector
from unittest.mock import patch, MagicMock
from datetime import datetime
from decimal import Decimal
from BankingRewardsFees_New.AWS_Lambda_Microservices.Account_Service import (
    convert_account_data,
    serialize_datetime,
    get_connection,
    lambda_handler
)

class TestSerializeDateTime(unittest.TestCase):
    
    def test_serialize_datetime_with_datetime(self):
        # Arrange
        test_datetime = datetime(2023, 5, 15, 10, 30, 45)
        expected_result = "2023-05-15 10:30:45"
        
        # Act
        result = serialize_datetime(test_datetime)
        
        # Assert
        self.assertEqual(result, expected_result)
    
    def test_serialize_datetime_with_decimal(self):
        # Arrange
        test_decimal = Decimal('123.45')
        expected_result = 123.45
        
        # Act
        result = serialize_datetime(test_decimal)
        
        # Assert
        self.assertEqual(result, expected_result)
        self.assertIsInstance(result, float)
    
    def test_serialize_datetime_with_other_types(self):
        # Arrange
        test_cases = [
            ("string", "string"),
            (123, 123),
            ([1, 2, 3], [1, 2, 3]),
            ({"key": "value"}, {"key": "value"}),
            (None, None)
        ]
        
        # Act & Assert
        for input_value, expected_result in test_cases:
            result = serialize_datetime(input_value)
            self.assertEqual(result, expected_result)
            
    def test_serialize_datetime_with_zero_decimal(self):
        # Arrange
        test_decimal = Decimal('0.0')
        expected_result = 0.0
        
        # Act
        result = serialize_datetime(test_decimal)
        
        # Assert
        self.assertEqual(result, expected_result)
        self.assertIsInstance(result, float)


class TestConvertAccountData(unittest.TestCase):
    
    def test_convert_account_data_with_none(self):
        # Arrange
        account_dict = None
        
        # Act
        result = convert_account_data(account_dict)
        
        # Assert
        self.assertIsNone(result)
    
    def test_convert_account_data_with_empty_dict(self):
        # Arrange
        account_dict = {}
        
        # Act
        result = convert_account_data(account_dict)
        
        # Assert
        self.assertEqual(result, {})
    
    def test_convert_account_data_with_non_datetime_values(self):
        # Arrange
        account_dict = {
            'id': 123,
            'name': 'Test Account',
            'balance': 1000.50,
            'active': True
        }
        
        # Act
        with patch('BankingRewardsFees_New.AWS_Lambda_Microservices.Account_Service.serialize_datetime') as mock_serialize:
            mock_serialize.side_effect = lambda x: x
            result = convert_account_data(account_dict)
        
        # Assert
        self.assertEqual(result, account_dict)
        self.assertEqual(mock_serialize.call_count, 4)
    
    def test_convert_account_data_with_datetime_values(self):
        # Arrange
        now = datetime.now()
        account_dict = {
            'id': 123,
            'created_at': now,
            'updated_at': now,
            'name': 'Test Account'
        }
        
        # Act
        with patch('BankingRewardsFees_New.AWS_Lambda_Microservices.Account_Service.serialize_datetime') as mock_serialize:
            mock_serialize.side_effect = lambda x: x.isoformat() if isinstance(x, datetime) else x
            result = convert_account_data(account_dict)
        
        # Assert
        expected = {
            'id': 123,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'name': 'Test Account'
        }
        self.assertEqual(result, expected)
        self.assertEqual(mock_serialize.call_count, 4)
    
    def test_convert_account_data_integration(self):
        # Arrange
        now = datetime.now()
        account_dict = {
            'id': 123,
            'created_at': now,
            'name': 'Test Account'
        }
        
        # Act
        result = convert_account_data(account_dict)
        
        # Assert
        expected = {
            'id': 123,
            'created_at': serialize_datetime(now),
            'name': 'Test Account'
        }
        self.assertEqual(result, expected)


class TestGetConnection(unittest.TestCase):
    
    @patch('mysql.connector.connect')
    def test_get_connection_default_values(self, mock_connect):
        # Arrange
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        # Act
        result = get_connection()
        
        # Assert
        mock_connect.assert_called_once_with(
            host='database-2.crq7shsasjo0.us-west-2.rds.amazonaws.com',
            user='admin',
            password='demo1234!',
            database='BankingRewardsFees_New',
            autocommit=True
        )
        self.assertEqual(result, mock_connection)
    
    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'test-host',
        'DB_USER': 'test-user',
        'DB_PASSWORD': 'test-password',
        'DB_NAME': 'test-database'
    })
    def test_get_connection_with_environment_variables(self, mock_connect):
        # Arrange
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        # Act
        result = get_connection()
        
        # Assert
        mock_connect.assert_called_once_with(
            host='test-host',
            user='test-user',
            password='test-password',
            database='test-database',
            autocommit=True
        )
        self.assertEqual(result, mock_connection)
    
    @patch('mysql.connector.connect')
    def test_get_connection_handles_connection_error(self, mock_connect):
        # Arrange
        mock_connect.side_effect = mysql.connector.Error("Connection error")
        
        # Act & Assert
        with self.assertRaises(mysql.connector.Error):
            get_connection()


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
        result = lambda_handler({'body': event}, None)
        
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
        result = lambda_handler({'body': event}, None)
        
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
        result = lambda_handler({'body': event}, None)
        
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
        result = lambda_handler({'body': event}, None)
        
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
        result = lambda_handler({'body': event}, None)
        
        # Assert
        self.assertEqual(result, {'error': 'Account not found'})
    
    def test_invalid_action(self):
        # Arrange
        event = {'action': 'invalid_action'}
        
        # Act
        result = lambda_handler({'body': event}, None)
        
        # Assert
        self.assertEqual(result, {'error': 'Invalid action: invalid_action. Available actions: get_accounts, get_account_details, update_balance'})
    
    @patch('mysql.connector.connect')
    def test_missing_account_id_for_get_account_details(self, mock_connect):
        # Arrange
        event = {'action': 'get_account_details'}
        
        # Act
        result = lambda_handler({'body': event}, None)
        
        # Assert
        self.assertEqual(result, {'error': 'account_id is required'})
        mock_connect.assert_not_called()
    
    @patch('mysql.connector.connect')
    def test_missing_parameters_for_update_balance(self, mock_connect):
        # Arrange
        event = {'action': 'update_balance', 'account_id': 1}  # Missing new_balance
        
        # Act
        result = lambda_handler({'body': event}, None)
        
        # Assert
        self.assertEqual(result, {'error': 'account_id and new_balance are required'})
        mock_connect.assert_not_called()
    
    @patch('mysql.connector.connect')
    def test_database_error(self, mock_connect):
        # Arrange
        mock_connect.side_effect = Exception("Database connection error")
        event = {'action': 'get_accounts'}
        
        # Act
        result = lambda_handler({'body': event}, None)
        
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
            lambda_handler(event, None)
            
            # Assert
            mock_connect.assert_called_once()
            mock_conn.cursor.assert_called_once_with(dictionary=True)


if __name__ == '__main__':
    unittest.main()