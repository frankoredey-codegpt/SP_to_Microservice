# Banking Rewards and Fees Management System - Requirements Document

## Executive Summary

The Banking Rewards and Fees Management System is a legacy Streamlit web application that manages customer banking accounts, calculates monthly fees and rewards, and provides account balance management functionality. The system uses MySQL stored procedures for business logic and serves as a demonstration of traditional monolithic banking application architecture.

## Business Overview

### Purpose
The application serves as a banking management tool that allows bank staff to:
- View and select customer accounts
- Calculate monthly fees based on customer tier and balance
- Calculate monthly rewards based on account balance
- Update account balances manually
- View comprehensive account details

### Business Context
This is a legacy system that demonstrates traditional banking operations with embedded business logic in database stored procedures. The system is designed to be migrated to a modern microservices architecture.

## Functional Requirements

### FR-001: Account Management
- **Description**: The system shall provide account selection and viewing capabilities
- **Acceptance Criteria**:
  - Display a dropdown list of all customer accounts showing customer name and account ID
  - Allow selection of a specific account for operations
  - Display comprehensive account details including balance, fees, and rewards

### FR-002: Monthly Fee Calculation
- **Description**: The system shall calculate monthly fees based on business rules
- **Business Rules**:
  - Premium tier customers: $0.00 monthly fee
  - Standard tier customers with balance > $5,000: $5.00 monthly fee
  - Standard tier customers with balance ≤ $5,000: $15.00 monthly fee
- **Acceptance Criteria**:
  - Execute fee calculation on demand via button click
  - Update the monthly_fees field in the database
  - Provide user feedback on successful calculation

### FR-003: Monthly Rewards Calculation
- **Description**: The system shall calculate monthly rewards based on account balance
- **Business Rules**:
  - Accounts with balance > $10,000: 2% of balance as rewards
  - Accounts with balance ≤ $10,000: 1% of balance as rewards
- **Acceptance Criteria**:
  - Execute rewards calculation on demand via button click
  - Update the monthly_rewards field in the database
  - Provide user feedback on successful calculation

### FR-004: Balance Management
- **Description**: The system shall allow manual balance updates
- **Acceptance Criteria**:
  - Display current balance in an editable number input field
  - Allow decimal precision to 2 places
  - Update balance in database upon save action
  - Refresh account details after balance update

### FR-005: Account Details Display
- **Description**: The system shall display comprehensive account information
- **Acceptance Criteria**:
  - Show all account fields except balance (handled separately)
  - Display data in a tabular format
  - Refresh data after any updates

## Non-Functional Requirements

### NFR-001: Performance
- Response time for database operations should be under 2 seconds
- Support concurrent access by multiple users

### NFR-002: Reliability
- Database connections should be properly managed (open/close)
- Error handling for database connectivity issues

### NFR-003: Usability
- Simple, intuitive web interface
- Clear feedback messages for user actions
- Responsive design suitable for desktop use

### NFR-004: Security
- Database credentials embedded in application (legacy approach)
- No authentication/authorization implemented (demo system)

## Technical Requirements

### Technology Stack
- **Frontend**: Streamlit web framework
- **Backend**: Python 3.x
- **Database**: MySQL 8.0
- **Dependencies**: 
  - streamlit
  - mysql-connector-python
  - pandas

### Database Schema

#### Accounts Table
```sql
CREATE TABLE Accounts (
    account_id INT PRIMARY KEY,
    customer_name VARCHAR(255),
    customer_tier VARCHAR(50), -- 'standard' or 'premium'
    balance DECIMAL(15,2),
    monthly_fees DECIMAL(10,2),
    monthly_rewards DECIMAL(10,2),
    legacy_flag CHAR(1), -- 'Y' or 'N'
    created_at DATETIME,
    updated_at DATETIME
);

Stored Procedures

CREATE PROCEDURE CalculateMonthlyFees(IN acc_id INT)
BEGIN
    DECLARE fee DECIMAL(10,2);
    
    IF (SELECT customer_tier FROM Accounts WHERE account_id = acc_id) = 'premium' THEN
        SET fee = 0.00;
    ELSEIF (SELECT balance FROM Accounts WHERE account_id = acc_id) > 5000 THEN
        SET fee = 5.00;
    ELSE
        SET fee = 15.00;
    END IF;
    
    UPDATE Accounts
    SET monthly_fees = fee
    WHERE account_id = acc_id;
END

CREATE PROCEDURE CalculateRewards(IN acc_id INT)
BEGIN
    DECLARE reward DECIMAL(10,2);
    DECLARE bal DECIMAL(15,2);
    
    SELECT balance INTO bal FROM Accounts WHERE account_id = acc_id;
    
    IF bal > 10000 THEN
        SET reward = bal * 0.02;
    ELSE
        SET reward = bal * 0.01;
    END IF;
    
    UPDATE Accounts
    SET monthly_rewards = reward
    WHERE account_id = acc_id;
END

Database Configuration
Host: database-2.crq7shsasjo0.us-west-2.rds.amazonaws.com
Database: BankingRewardsFees_Old
User: admin
Password: demo1234!
Data Model
Customer Tiers
Standard: Default tier with standard fee structure
Premium: Enhanced tier with waived monthly fees
Sample Data Structure
{
  "account_id": 1,
  "customer_name": "Alice Johnson",
  "customer_tier": "standard",
  "balance": "1200.00",
  "monthly_fees": "15.00",
  "monthly_rewards": "12.00",
  "legacy_flag": "Y",
  "created_at": "2025-07-10T18:56:52.000Z",
  "updated_at": "2025-07-10T18:56:52.000Z"
}

Business Logic Rules
Fee Calculation Logic
Check customer tier
If premium tier → $0 fee
If standard tier → check balance
If balance > $5,000 → $5 fee
If balance ≤ $5,000 → $15 fee
Rewards Calculation Logic
Get current account balance
If balance > $10,000 → 2% rewards rate
If balance ≤ $10,000 → 1% rewards rate
Calculate: balance × rate = monthly rewards
Legacy Components
Deprecated Features
CalculateReferralBonus: No longer used by business
LegacyAccountCleanup: Legacy flag management (unused)
legacy_flag: Column maintained for historical purposes
Migration Notes
Business logic currently embedded in stored procedures
Data structure combines customer and account information in single table
Manual balance management indicates lack of transaction processing
No audit trail or transaction history
User Interface Requirements
Main Interface Components
Title: "Banking Rewards & Fees Demo (Legacy SP Version)"
Account Selector: Dropdown showing "Customer Name (ID: account_id)"
Action Buttons:
"Calculate Fees"
"Calculate Rewards"
"Save Balance"
Account Details Section:
Editable balance field
Read-only account information table
User Workflow
Select account from dropdown
View current account details
Optionally calculate fees or rewards
Optionally update balance
View updated account information
Integration Requirements
Database Integration
Direct MySQL connection using mysql-connector-python
Connection pooling not implemented (single connection per operation)
Manual connection management (open/close per operation)
External Dependencies
No external API integrations
No third-party service dependencies
Self-contained application
Constraints and Limitations
Technical Constraints
Single-user interface design
No concurrent operation handling
Embedded database credentials
No configuration management
Limited error handling
Business Constraints
Demo/legacy system - not production-ready
No real-time transaction processing
Manual balance updates only
No audit trail or compliance features
Future Migration Considerations
Microservices Architecture Target
Based on data_mapping.json, the future system should:

Separate customer and account data into distinct entities
Move business logic from stored procedures to Python microservices
Remove deprecated columns (monthly_fees, monthly_rewards, legacy_flag)
Implement proper customer-account relationships via foreign keys
Enable real-time calculation services instead of stored values
Recommended Microservices
Customer Service: Manage customer information and tiers
Account Service: Handle account data and balances
Fee Calculation Service: Calculate fees based on business rules
Rewards Calculation Service: Calculate rewards based on balance
Transaction Service: Handle balance updates and transaction history