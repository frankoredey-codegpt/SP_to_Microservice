import unittest
from unittest.mock import patch, MagicMock, Mock
import json
import requests
import sys
import os

# Add the parent directory to sys.path to allow importing the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions from app.py
from BankingRewardsFees_New.app import (
    call_account_service,
    call_fee_calculation_service,
    call_rewards_calculation_service,
    get_accounts,
    get_account_details,
    update_account_balance,
    ACCOUNT_SERVICE_URL,
    FEE_CALCULATION_URL,
    REWARDS_CALCULATION_URL
)

class TestBankingApp(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_account_data = [
            {
                'account_id': 1,
                'customer_name': 'John Doe',
                'customer_id': 100,
                'balance': 5000.00,
                'customer_tier': 'gold'
            },
            {
                'account_id': 2,
                'customer_name': 'Jane Smith',
                'customer_id': 101,
                'balance': 15000.00,
                'customer_tier': 'premium'
            }
        ]
        
        self.sample_account_details = {
            'account_id': 1,
            'customer_name': 'John Doe',
            'customer_id': 100,
            'balance': 5000.00,
            'customer_tier': 'gold',
            'created_at': '2023-01-01 12:00:00',
            'updated_at': '2023-01-02 12:00:00'
        }
        
        self.sample_fee_result = {
            'account_id': 1,
            'calculated_fee': 15.00,
            'customer_tier': 'gold',
            'balance': 5000.00
        }
        
        self.sample_reward_result = {
            'account_id': 1,
            'calculated_reward': 50.00,
            'balance': 5000.00
        }

    def test_service_urls_defined(self):
        """Test that service URLs are properly defined"""
        self.assertIsInstance(ACCOUNT_SERVICE_URL, str)
        self.assertIsInstance(FEE_CALCULATION_URL, str)
        self.assertIsInstance(REWARDS_CALCULATION_URL, str)
        self.assertTrue(ACCOUNT_SERVICE_URL.startswith('https://'))
        self.assertTrue(FEE_CALCULATION_URL.startswith('https://'))
        self.assertTrue(REWARDS_CALCULATION_URL.startswith('https://'))

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_account_service_success_direct_response(self, mock_st, mock_post):
        """Test successful call to account service with direct response format"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_account_data
        mock_post.return_value = mock_response

        result = call_account_service("get_accounts")

        self.assertEqual(result, self.sample_account_data)
        mock_post.assert_called_once_with(
            ACCOUNT_SERVICE_URL,
            json={"action": "get_accounts"}
        )

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_account_service_success_lambda_body_format(self, mock_st, mock_post):
        """Test successful call to account service with Lambda body format"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'body': json.dumps(self.sample_account_data)
        }
        mock_post.return_value = mock_response

        result = call_account_service("get_accounts")

        self.assertEqual(result, self.sample_account_data)

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_account_service_success_lambda_body_dict_format(self, mock_st, mock_post):
        """Test successful call to account service with Lambda body as dict"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'body': self.sample_account_data
        }
        mock_post.return_value = mock_response

        result = call_account_service("get_accounts")

        self.assertEqual(result, self.sample_account_data)

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_account_service_with_kwargs(self, mock_st, mock_post):
        """Test call to account service with additional keyword arguments"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_account_details
        mock_post.return_value = mock_response

        result = call_account_service("get_account_details", account_id=1)

        self.assertEqual(result, self.sample_account_details)
        mock_post.assert_called_once_with(
            ACCOUNT_SERVICE_URL,
            json={"action": "get_account_details", "account_id": 1}
        )

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_account_service_http_error(self, mock_st, mock_post):
        """Test account service call with HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = call_account_service("get_accounts")

        self.assertIsNone(result)
        mock_st.error.assert_called_once_with("Account service error: 500 - Internal Server Error")

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_account_service_json_decode_error(self, mock_st, mock_post):
        """Test account service call with JSON decode error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response

        result = call_account_service("get_accounts")

        self.assertIsNone(result)
        mock_st.error.assert_called_once()
        self.assertTrue("JSON decode error" in str(mock_st.error.call_args[0][0]))

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_account_service_request_exception(self, mock_st, mock_post):
        """Test account service call with request exception"""
        mock_post.side_effect = requests.RequestException("Connection error")

        result = call_account_service("get_accounts")

        self.assertIsNone(result)
        mock_st.error.assert_called_once()
        self.assertTrue("Error calling account service" in str(mock_st.error.call_args[0][0]))

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_fee_calculation_service_success(self, mock_st, mock_post):
        """Test successful call to fee calculation service"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_fee_result
        mock_post.return_value = mock_response

        result = call_fee_calculation_service(1)

        self.assertEqual(result, self.sample_fee_result)
        mock_post.assert_called_once_with(
            FEE_CALCULATION_URL,
            json={"account_id": 1}
        )

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_fee_calculation_service_lambda_body_format(self, mock_st, mock_post):
        """Test fee calculation service with Lambda body format"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'body': json.dumps(self.sample_fee_result)
        }
        mock_post.return_value = mock_response

        result = call_fee_calculation_service(1)

        self.assertEqual(result, self.sample_fee_result)

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_fee_calculation_service_http_error(self, mock_st, mock_post):
        """Test fee calculation service with HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_post.return_value = mock_response

        result = call_fee_calculation_service(999)

        self.assertIsNone(result)
        mock_st.error.assert_called_once_with("Fee calculation service error: 404 - Not Found")

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_rewards_calculation_service_success(self, mock_st, mock_post):
        """Test successful call to rewards calculation service"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_reward_result
        mock_post.return_value = mock_response

        result = call_rewards_calculation_service(1)

        self.assertEqual(result, self.sample_reward_result)
        mock_post.assert_called_once_with(
            REWARDS_CALCULATION_URL,
            json={"account_id": 1}
        )

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_rewards_calculation_service_lambda_body_format(self, mock_st, mock_post):
        """Test rewards calculation service with Lambda body format"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'body': self.sample_reward_result
        }
        mock_post.return_value = mock_response

        result = call_rewards_calculation_service(1)

        self.assertEqual(result, self.sample_reward_result)

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_call_rewards_calculation_service_json_error(self, mock_st, mock_post):
        """Test rewards calculation service with JSON error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response

        result = call_rewards_calculation_service(1)

        self.assertIsNone(result)
        mock_st.error.assert_called_once()
        self.assertTrue("JSON decode error" in str(mock_st.error.call_args[0][0]))

    @patch('BankingRewardsFees_New.app.call_account_service')
    def test_get_accounts_success(self, mock_call_service):
        """Test successful get_accounts helper function"""
        mock_call_service.return_value = self.sample_account_data

        result = get_accounts()

        self.assertEqual(result, self.sample_account_data)
        mock_call_service.assert_called_once_with("get_accounts")

    @patch('BankingRewardsFees_New.app.call_account_service')
    def test_get_accounts_failure(self, mock_call_service):
        """Test get_accounts helper function with service failure"""
        mock_call_service.return_value = None

        result = get_accounts()

        self.assertIsNone(result)
        mock_call_service.assert_called_once_with("get_accounts")

    @patch('BankingRewardsFees_New.app.call_account_service')
    def test_get_account_details_success(self, mock_call_service):
        """Test successful get_account_details helper function"""
        mock_call_service.return_value = self.sample_account_details

        result = get_account_details(1)

        self.assertEqual(result, self.sample_account_details)
        mock_call_service.assert_called_once_with("get_account_details", account_id=1)

    @patch('BankingRewardsFees_New.app.call_account_service')
    def test_get_account_details_not_found(self, mock_call_service):
        """Test get_account_details helper function when account not found"""
        mock_call_service.return_value = None

        result = get_account_details(999)

        self.assertIsNone(result)
        mock_call_service.assert_called_once_with("get_account_details", account_id=999)

    @patch('BankingRewardsFees_New.app.call_account_service')
    def test_update_account_balance_success(self, mock_call_service):
        """Test successful update_account_balance helper function"""
        expected_result = {"message": "Balance updated successfully"}
        mock_call_service.return_value = expected_result

        result = update_account_balance(1, 6000.00)

        self.assertEqual(result, expected_result)
        mock_call_service.assert_called_once_with("update_balance", account_id=1, new_balance=6000.00)

    @patch('BankingRewardsFees_New.app.call_account_service')
    def test_update_account_balance_failure(self, mock_call_service):
        """Test update_account_balance helper function with service failure"""
        mock_call_service.return_value = None

        result = update_account_balance(1, 6000.00)

        self.assertIsNone(result)
        mock_call_service.assert_called_once_with("update_balance", account_id=1, new_balance=6000.00)

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_all_services_different_error_handling(self, mock_st, mock_post):
        """Test that all service functions handle different types of errors consistently"""
        # Test connection timeout
        mock_post.side_effect = requests.Timeout("Request timeout")

        # Test account service
        result1 = call_account_service("get_accounts")
        self.assertIsNone(result1)

        # Test fee calculation service
        result2 = call_fee_calculation_service(1)
        self.assertIsNone(result2)

        # Test rewards calculation service
        result3 = call_rewards_calculation_service(1)
        self.assertIsNone(result3)

        # All should have called st.error
        self.assertEqual(mock_st.error.call_count, 3)

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_response_format_edge_cases(self, mock_st, mock_post):
        """Test edge cases in response format handling"""
        # Test empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        result = call_account_service("get_accounts")
        self.assertEqual(result, {})

        # Test response with body as empty string
        mock_response.json.return_value = {'body': ''}
        result = call_account_service("get_accounts")
        self.assertIsNone(result)  # Empty string should cause JSON decode error

        # Test response with body as None
        mock_response.json.return_value = {'body': None}
        result = call_account_service("get_accounts")
        self.assertIsNone(result)

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_service_payload_construction(self, mock_st, mock_post):
        """Test that service payloads are constructed correctly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        # Test account service with multiple kwargs
        call_account_service("update_balance", account_id=1, new_balance=5000.00, extra_param="test")
        
        expected_payload = {
            "action": "update_balance",
            "account_id": 1,
            "new_balance": 5000.00,
            "extra_param": "test"
        }
        mock_post.assert_called_with(ACCOUNT_SERVICE_URL, json=expected_payload)

        # Test fee calculation service
        call_fee_calculation_service(123)
        mock_post.assert_called_with(FEE_CALCULATION_URL, json={"account_id": 123})

        # Test rewards calculation service
        call_rewards_calculation_service(456)
        mock_post.assert_called_with(REWARDS_CALCULATION_URL, json={"account_id": 456})

    def test_helper_functions_parameter_passing(self):
        """Test that helper functions pass parameters correctly"""
        with patch('BankingRewardsFees_New.app.call_account_service') as mock_call:
            mock_call.return_value = {"test": "data"}

            # Test get_accounts
            get_accounts()
            mock_call.assert_called_with("get_accounts")

            # Test get_account_details
            get_account_details(42)
            mock_call.assert_called_with("get_account_details", account_id=42)

            # Test update_account_balance
            update_account_balance(99, 1234.56)
            mock_call.assert_called_with("update_balance", account_id=99, new_balance=1234.56)

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_malformed_json_response_handling(self, mock_st, mock_post):
        """Test handling of malformed JSON in Lambda body responses"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'body': '{"invalid": json}'  # Malformed JSON
        }
        mock_post.return_value = mock_response

        result = call_account_service("get_accounts")
        
        self.assertIsNone(result)
        mock_st.error.assert_called_once()
        self.assertTrue("JSON decode error" in str(mock_st.error.call_args[0][0]))

    @patch('BankingRewardsFees_New.app.requests.post')
    @patch('BankingRewardsFees_New.app.st')
    def test_service_response_data_types(self, mock_st, mock_post):
        """Test handling of different response data types"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Test list response
        mock_response.json.return_value = [1, 2, 3]
        result = call_account_service("get_accounts")
        self.assertEqual(result, [1, 2, 3])

        # Test dict response without body
        mock_response.json.return_value = {"key": "value"}
        result = call_account_service("get_accounts")
        self.assertEqual(result, {"key": "value"})

        # Test string response (should be returned as-is)
        mock_response.json.return_value = "string_response"
        result = call_account_service("get_accounts")
        self.assertEqual(result, "string_response")

if __name__ == '__main__':
    unittest.main()
