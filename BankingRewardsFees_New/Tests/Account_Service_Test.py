import unittest
from unittest.mock import patch, MagicMock
import account_service
import json

class TestAccountService(unittest.TestCase):

    @patch('account_service.mysql.connector.connect')
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

        event = {
            'body': json.dumps({'action': 'get_accounts'})
        }
        result = account_service.lambda_handler(event, None)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['customer_name'], 'John Doe')
        mock_cursor.execute.assert_called()

    @patch('account_service.mysql.connector.connect')
    def test_get_account_details_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetchone result
        mock_cursor.fetchone.return_value = {
            'account_id': 1,
            'customer_id': 100,
            'balance': 500.0,
            'created_at': None,
            'updated_at': None,
            'customer_name': 'John Doe',
            'customer_tier': 'Gold'
        }

        event = {
            'body': json.dumps({'action': 'get_account_details', 'account_id': 1})
        }
        result = account_service.lambda_handler(event, None)

        self.assertIn('account_id', result)
        self.assertEqual(result['customer_name'], 'John Doe')
        mock_cursor.execute.assert_called()

    @patch('account_service.mysql.connector.connect')
    def test_get_account_details_missing_id(self, mock_connect):
        event = {
            'body': json.dumps({'action': 'get_account_details'})
        }
        result = account_service.lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'account_id is required')

    @patch('account_service.mysql.connector.connect')
    def test_get_account_details_not_found(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        event = {
            'body': json.dumps({'action': 'get_account_details', 'account_id': 999})
        }
        result = account_service.lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Account not found')

    @patch('account_service.mysql.connector.connect')
    def test_update_balance_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.rowcount = 1

        event = {
            'body': json.dumps({'action': 'update_balance', 'account_id': 1, 'new_balance': 1000.0})
        }
        result = account_service.lambda_handler(event, None)

        self.assertIn('message', result)
        self.assertEqual(result['message'], 'Balance updated successfully')
        mock_cursor.execute.assert_called()

    @patch('account_service.mysql.connector.connect')
    def test_update_balance_missing_fields(self, mock_connect):
        event = {
            'body': json.dumps({'action': 'update_balance'})
        }
        result = account_service.lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'account_id and new_balance are required')

    @patch('account_service.mysql.connector.connect')
    def test_update_balance_account_not_found(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.rowcount = 0

        event = {
            'body': json.dumps({'action': 'update_balance', 'account_id': 999, 'new_balance': 1000.0})
        }
        result = account_service.lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Account not found')

    def test_invalid_action(self):
        event = {
            'body': json.dumps({'action': 'non_existing_action'})
        }
        result = account_service.lambda_handler(event, None)

        self.assertIn('error', result)
        self.assertTrue('Invalid action' in result['error'])

if __name__ == '__main__':
    unittest.main()
