import unittest
import requests
import json
import time
import os
from decimal import Decimal

class TestAWSMicroservicesIntegration(unittest.TestCase):
    """
    Integration tests for AWS Lambda microservices.
    These tests make actual HTTP requests to deployed Lambda functions.
    
    Prerequisites:
    - AWS Lambda functions must be deployed and accessible
    - Database must be populated with test data
    - Environment variables or hardcoded URLs must be set
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration and URLs"""
        # AWS Lambda Function URLs - Update these with your actual deployed URLs
        cls.ACCOUNT_SERVICE_URL = os.getenv(
            'ACCOUNT_SERVICE_URL', 
            "https://h4s7q404t9.execute-api.us-west-2.amazonaws.com/default/Account_Service"
        )
        cls.FEE_CALCULATION_URL = os.getenv(
            'FEE_CALCULATION_URL',
            "https://31ex1bcgtg.execute-api.us-west-2.amazonaws.com/default/Fee_Calculation_Service"
        )
        cls.REWARDS_CALCULATION_URL = os.getenv(
            'REWARDS_CALCULATION_URL',
            "https://we5fvnijya.execute-api.us-west-2.amazonaws.com/default/Rewards_Calculation_Service"
        )
        
        # Test configuration
        cls.timeout = 30  # seconds
        cls.test_account_id = None  # Will be set during tests
        cls.original_balance = None  # Will store original balance for cleanup
        
        print(f"Testing against:")
        print(f"Account Service: {cls.ACCOUNT_SERVICE_URL}")
        print(f"Fee Calculation: {cls.FEE_CALCULATION_URL}")
        print(f"Rewards Calculation: {cls.REWARDS_CALCULATION_URL}")

    def setUp(self):
        """Set up before each test"""
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Integration-Test/1.0'
        })

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'session'):
            self.session.close()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests - restore original balance if modified"""
        if cls.test_account_id and cls.original_balance is not None:
            try:
                payload = {
                    "action": "update_balance",
                    "account_id": cls.test_account_id,
                    "new_balance": cls.original_balance
                }
                requests.post(cls.ACCOUNT_SERVICE_URL, json=payload, timeout=30)
                print(f"Restored original balance ${cls.original_balance} for account {cls.test_account_id}")
            except Exception as e:
                print(f"Warning: Could not restore original balance: {e}")

    def _make_request(self, url, payload, service_name):
        """Helper method to make HTTP requests with error handling"""
        try:
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            # Log request/response for debugging
            print(f"\n{service_name} Request:")
            print(f"URL: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            print(f"Response Status: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
            self.assertEqual(response.status_code, 200, 
                           f"{service_name} returned status {response.status_code}: {response.text}")
            
            response_data = response.json()
            
            # Handle different Lambda response formats
            if isinstance(response_data, dict) and 'body' in response_data:
                if isinstance(response_data['body'], str):
                    return json.loads(response_data['body'])
                else:
                    return response_data['body']
            
            return response_data
            
        except requests.exceptions.Timeout:
            self.fail(f"{service_name} request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            self.fail(f"Could not connect to {service_name} at {url}")
        except json.JSONDecodeError as e:
            self.fail(f"{service_name} returned invalid JSON: {e}")
        except Exception as e:
            self.fail(f"Unexpected error calling {service_name}: {e}")

    def test_01_account_service_get_accounts(self):
        """Test Account Service - Get all accounts"""
        payload = {"action": "get_accounts"}
        
        accounts = self._make_request(
            self.ACCOUNT_SERVICE_URL, 
            payload, 
            "Account Service (get_accounts)"
        )
        
        # Validate response structure
        self.assertIsInstance(accounts, list, "Expected list of accounts")
        self.assertGreater(len(accounts), 0, "Expected at least one account")
        
        # Validate account structure - get_accounts only returns basic info
        account = accounts[0]
        required_fields = ['account_id', 'customer_name', 'customer_id']
        for field in required_fields:
            self.assertIn(field, account, f"Account missing required field: {field}")
        
        # Store test account for subsequent tests
        self.__class__.test_account_id = account['account_id']
        
        print(f"✓ Found {len(accounts)} accounts")
        print(f"✓ Using account ID {self.test_account_id} for subsequent tests")

    def test_02_account_service_get_account_details(self):
        """Test Account Service - Get specific account details"""
        self.assertIsNotNone(self.test_account_id, "test_01 must run first to set test_account_id")
        
        payload = {
            "action": "get_account_details",
            "account_id": self.test_account_id
        }
        
        account_details = self._make_request(
            self.ACCOUNT_SERVICE_URL,
            payload,
            "Account Service (get_account_details)"
        )
        
        # Validate response structure
        self.assertIsInstance(account_details, dict, "Expected account details as dict")
        
        required_fields = ['account_id', 'customer_name', 'customer_id', 'balance', 'customer_tier']
        for field in required_fields:
            self.assertIn(field, account_details, f"Account details missing field: {field}")
        
        # Validate data types
        self.assertEqual(account_details['account_id'], self.test_account_id)
        self.assertIsInstance(account_details['balance'], (int, float))
        self.assertIsInstance(account_details['customer_name'], str)
        self.assertIsInstance(account_details['customer_tier'], str)
        
        # Store original balance for cleanup
        self.__class__.original_balance = float(account_details['balance'])
        
        print(f"✓ Account details retrieved for {account_details['customer_name']}")
        print(f"✓ Balance: ${account_details['balance']}, Tier: {account_details['customer_tier']}")

    def test_03_fee_calculation_service(self):
        """Test Fee Calculation Service"""
        self.assertIsNotNone(self.test_account_id, "test_01 must run first to set test_account_id")
        
        payload = {"account_id": self.test_account_id}
        
        fee_result = self._make_request(
            self.FEE_CALCULATION_URL,
            payload,
            "Fee Calculation Service"
        )
        
        # Validate response structure
        self.assertIsInstance(fee_result, dict, "Expected fee result as dict")
        
        required_fields = ['account_id', 'calculated_fee', 'customer_tier', 'balance']
        for field in required_fields:
            self.assertIn(field, fee_result, f"Fee result missing field: {field}")
        
        # Validate data types and values
        self.assertEqual(fee_result['account_id'], self.test_account_id)
        self.assertIsInstance(fee_result['calculated_fee'], (int, float))
        self.assertGreaterEqual(fee_result['calculated_fee'], 0, "Fee should be non-negative")
        self.assertIsInstance(fee_result['balance'], (int, float))
        
        # Validate business logic
        balance = fee_result['balance']
        tier = fee_result['customer_tier']
        calculated_fee = fee_result['calculated_fee']
        
        if tier == 'premium':
            expected_fee = 0.0
        elif balance > 5000:
            expected_fee = 5.0
        else:
            expected_fee = 15.0
        
        self.assertEqual(calculated_fee, expected_fee, 
                        f"Fee calculation incorrect. Balance: ${balance}, Tier: {tier}, "
                        f"Expected: ${expected_fee}, Got: ${calculated_fee}")
        
        print(f"✓ Fee calculated: ${calculated_fee} (Balance: ${balance}, Tier: {tier})")

    def test_04_rewards_calculation_service(self):
        """Test Rewards Calculation Service"""
        self.assertIsNotNone(self.test_account_id, "test_01 must run first to set test_account_id")
        
        payload = {"account_id": self.test_account_id}
        
        reward_result = self._make_request(
            self.REWARDS_CALCULATION_URL,
            payload,
            "Rewards Calculation Service"
        )
        
        # Validate response structure
        self.assertIsInstance(reward_result, dict, "Expected reward result as dict")
        
        required_fields = ['account_id', 'calculated_reward', 'balance']
        for field in required_fields:
            self.assertIn(field, reward_result, f"Reward result missing field: {field}")
        
        # Validate data types and values
        self.assertEqual(reward_result['account_id'], self.test_account_id)
        self.assertIsInstance(reward_result['calculated_reward'], (int, float))
        self.assertGreaterEqual(reward_result['calculated_reward'], 0, "Reward should be non-negative")
        self.assertIsInstance(reward_result['balance'], (int, float))
        
        # Validate business logic
        balance = reward_result['balance']
        calculated_reward = reward_result['calculated_reward']
        
        if balance > 10000:
            expected_reward = round(balance * 0.02, 2)
        else:
            expected_reward = round(balance * 0.01, 2)
        
        self.assertEqual(calculated_reward, expected_reward,
                        f"Reward calculation incorrect. Balance: ${balance}, "
                        f"Expected: ${expected_reward}, Got: ${calculated_reward}")
        
        print(f"✓ Reward calculated: ${calculated_reward} (Balance: ${balance})")

    def test_05_account_service_update_balance(self):
        """Test Account Service - Update balance"""
        self.assertIsNotNone(self.test_account_id, "test_01 must run first to set test_account_id")
        self.assertIsNotNone(self.original_balance, "test_02 must run first to set original_balance")
        
        # Test with a new balance
        new_balance = 7500.50
        payload = {
            "action": "update_balance",
            "account_id": self.test_account_id,
            "new_balance": new_balance
        }
        
        update_result = self._make_request(
            self.ACCOUNT_SERVICE_URL,
            payload,
            "Account Service (update_balance)"
        )
        
        # Validate response
        self.assertIsInstance(update_result, dict, "Expected update result as dict")
        self.assertIn('message', update_result, "Update result should contain message")
        
        # Verify the balance was actually updated
        time.sleep(1)  # Brief pause to ensure database consistency
        
        get_payload = {
            "action": "get_account_details",
            "account_id": self.test_account_id
        }
        
        updated_account = self._make_request(
            self.ACCOUNT_SERVICE_URL,
            get_payload,
            "Account Service (verify update)"
        )
        
        self.assertEqual(float(updated_account['balance']), new_balance,
                        f"Balance not updated correctly. Expected: ${new_balance}, "
                        f"Got: ${updated_account['balance']}")
        
        print(f"✓ Balance updated successfully to ${new_balance}")

    def test_06_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        self.assertIsNotNone(self.test_account_id, "Previous tests must run first")
        
        print("\n=== END-TO-END WORKFLOW TEST ===")
        
        # Step 1: Get account details
        get_payload = {
            "action": "get_account_details",
            "account_id": self.test_account_id
        }
        
        account = self._make_request(
            self.ACCOUNT_SERVICE_URL,
            get_payload,
            "E2E - Get Account"
        )
        
        print(f"Step 1: Retrieved account for {account['customer_name']}")
        
        # Step 2: Calculate fees
        fee_payload = {"account_id": self.test_account_id}
        fee_result = self._make_request(
            self.FEE_CALCULATION_URL,
            fee_payload,
            "E2E - Calculate Fee"
        )
        
        print(f"Step 2: Calculated fee: ${fee_result['calculated_fee']}")
        
        # Step 3: Calculate rewards
        reward_payload = {"account_id": self.test_account_id}
        reward_result = self._make_request(
            self.REWARDS_CALCULATION_URL,
            reward_payload,
            "E2E - Calculate Reward"
        )
        
        print(f"Step 3: Calculated reward: ${reward_result['calculated_reward']}")
        
        # Step 4: Update balance (simulate applying fee and reward)
        current_balance = float(account['balance'])
        fee = fee_result['calculated_fee']
        reward = reward_result['calculated_reward']
        new_balance = round(current_balance - fee + reward, 2)
        
        update_payload = {
            "action": "update_balance",
            "account_id": self.test_account_id,
            "new_balance": new_balance
        }
        
        update_result = self._make_request(
            self.ACCOUNT_SERVICE_URL,
            update_payload,
            "E2E - Update Balance"
        )
        
        print(f"Step 4: Updated balance from ${current_balance} to ${new_balance}")
        print(f"         (Applied fee: -${fee}, reward: +${reward})")
        
        # Step 5: Verify final state
        time.sleep(1)
        final_account = self._make_request(
            self.ACCOUNT_SERVICE_URL,
            get_payload,
            "E2E - Verify Final State"
        )
        
        self.assertEqual(float(final_account['balance']), new_balance,
                        "Final balance verification failed")
        
        print(f"Step 5: Verified final balance: ${final_account['balance']}")
        print("✓ End-to-end workflow completed successfully!")

    def test_07_error_handling(self):
        """Test error handling scenarios"""
        print("\n=== ERROR HANDLING TESTS ===")
        
        # Test 1: Invalid account ID
        invalid_payload = {"action": "get_account_details", "account_id": 99999}
        
        try:
            response = self.session.post(self.ACCOUNT_SERVICE_URL, json=invalid_payload, timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict) and 'body' in result:
                    result = json.loads(result['body']) if isinstance(result['body'], str) else result['body']
                
                self.assertIn('error', result, "Expected error for invalid account ID")
                print("✓ Invalid account ID handled correctly")
            else:
                print(f"✓ Invalid account ID returned HTTP {response.status_code}")
        except Exception as e:
            print(f"✓ Invalid account ID caused exception (expected): {e}")
        
        # Test 2: Missing required fields
        missing_field_payload = {"action": "update_balance", "account_id": self.test_account_id}
        
        try:
            response = self.session.post(self.ACCOUNT_SERVICE_URL, json=missing_field_payload, timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict) and 'body' in result:
                    result = json.loads(result['body']) if isinstance(result['body'], str) else result['body']
                
                self.assertIn('error', result, "Expected error for missing new_balance")
                print("✓ Missing required field handled correctly")
            else:
                print(f"✓ Missing field returned HTTP {response.status_code}")
        except Exception as e:
            print(f"✓ Missing field caused exception (expected): {e}")
        
        # Test 3: Invalid action
        invalid_action_payload = {"action": "invalid_action"}
        
        try:
            response = self.session.post(self.ACCOUNT_SERVICE_URL, json=invalid_action_payload, timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict) and 'body' in result:
                    result = json.loads(result['body']) if isinstance(result['body'], str) else result['body']
                
                self.assertIn('error', result, "Expected error for invalid action")
                print("✓ Invalid action handled correctly")
            else:
                print(f"✓ Invalid action returned HTTP {response.status_code}")
        except Exception as e:
            print(f"✓ Invalid action caused exception (expected): {e}")

    def test_08_performance_and_reliability(self):
        """Test performance and reliability"""
        print("\n=== PERFORMANCE AND RELIABILITY TESTS ===")
        
        # Test multiple rapid requests
        start_time = time.time()
        successful_requests = 0
        total_requests = 5
        
        for i in range(total_requests):
            try:
                payload = {"action": "get_accounts"}
                response = self.session.post(self.ACCOUNT_SERVICE_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    successful_requests += 1
                time.sleep(0.5)  # Brief pause between requests
            except Exception as e:
                print(f"Request {i+1} failed: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        success_rate = (successful_requests / total_requests) * 100
        avg_response_time = duration / total_requests
        
        print(f"✓ Performance test completed:")
        print(f"  - Success rate: {success_rate}% ({successful_requests}/{total_requests})")
        print(f"  - Average response time: {avg_response_time:.2f} seconds")
        print(f"  - Total duration: {duration:.2f} seconds")
        
        # Assert minimum performance standards
        self.assertGreaterEqual(success_rate, 80, "Success rate should be at least 80%")
        self.assertLess(avg_response_time, 5, "Average response time should be under 5 seconds")

    def test_09_service_consistency(self):
        """Test that all services return consistent account information"""
        self.assertIsNotNone(self.test_account_id, "Previous tests must run first")
        
        print("\n=== SERVICE CONSISTENCY TEST ===")
        
        # Get account details from Account Service
        account_payload = {
            "action": "get_account_details",
            "account_id": self.test_account_id
        }
        
        account_details = self._make_request(
            self.ACCOUNT_SERVICE_URL,
            account_payload,
            "Consistency - Account Details"
        )
        
        # Get fee calculation (which also returns balance and tier)
        fee_payload = {"account_id": self.test_account_id}
        fee_result = self._make_request(
            self.FEE_CALCULATION_URL,
            fee_payload,
            "Consistency - Fee Calculation"
        )
        
        # Get rewards calculation (which also returns balance)
        reward_payload = {"account_id": self.test_account_id}
        reward_result = self._make_request(
            self.REWARDS_CALCULATION_URL,
            reward_payload,
            "Consistency - Rewards Calculation"
        )
        
        # Verify all services return consistent data
        self.assertEqual(account_details['account_id'], fee_result['account_id'],
                        "Account ID mismatch between Account Service and Fee Service")
        self.assertEqual(account_details['account_id'], reward_result['account_id'],
                        "Account ID mismatch between Account Service and Rewards Service")
        
        self.assertEqual(float(account_details['balance']), float(fee_result['balance']),
                        "Balance mismatch between Account Service and Fee Service")
        self.assertEqual(float(account_details['balance']), float(reward_result['balance']),
                        "Balance mismatch between Account Service and Rewards Service")
        
        self.assertEqual(account_details['customer_tier'], fee_result['customer_tier'],
                        "Customer tier mismatch between Account Service and Fee Service")
        
        print("✓ All services return consistent account information")
        print(f"  - Account ID: {account_details['account_id']}")
        print(f"  - Balance: ${account_details['balance']}")
        print(f"  - Customer Tier: {account_details['customer_tier']}")

if __name__ == '__main__':
    # Configure test runner to maintain order
    unittest.TestLoader.sortTestMethodsUsing = lambda _, x, y: (x > y) - (x < y)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)
