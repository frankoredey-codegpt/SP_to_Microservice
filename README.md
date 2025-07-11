"# Banking Rewards & Fees System - Stored Procedure to Microservice Migration

## Overview

This repository demonstrates the migration of a legacy monolithic banking application from stored procedure-based architecture to modern microservices using AWS Lambda functions. The project showcases the transformation of a traditional MySQL stored procedure system into a cloud-native, scalable microservices architecture.

## Repository Structure

```
├── BankingRewardsFees_Old/          # Legacy monolithic application
│   ├── app.py                       # Original Streamlit app with stored procedures
│   └── requirements.md              # Legacy requirements documentation
├── BankingRewardsFees_New/          # Modern microservices application
│   ├── app.py                       # New Streamlit app using Lambda functions
│   └── requirements.txt             # Python dependencies
├── Old_to_New_Migration/            # Migration documentation
│   └── data_mapping.json           # Schema mapping and migration guide
└── .vscode/                        # VS Code configuration
    └── settings.json
```

## Architecture Evolution

### Legacy Architecture (BankingRewardsFees_Old)
- **Frontend**: Streamlit web application
- **Backend**: Direct MySQL database connections
- **Business Logic**: MySQL stored procedures (`CalculateMonthlyFees`, `CalculateRewards`)
- **Database**: Single monolithic schema with combined customer/account data
- **Connection**: Direct database connection to `database-2.crq7shsasjo0.us-west-2.rds.amazonaws.com`

### Modern Architecture (BankingRewardsFees_New)
- **Frontend**: Streamlit web application (UI preserved)
- **Backend**: AWS Lambda microservices
- **Business Logic**: Python-based microservices
- **Database**: Normalized schema with separated customer and account entities
- **API Gateway**: RESTful endpoints for service communication

## Microservices

The new architecture implements three core microservices:

1. **Account Service** 
   - URL: `https://h4s7q404t9.execute-api.us-west-2.amazonaws.com/default/Account_Service`
   - Manages account data and customer information
   - Handles balance updates
   - Provides account details retrieval

2. **Fee Calculation Service**
   - URL: `https://31ex1bcgtg.execute-api.us-west-2.amazonaws.com/default/Fee_Calculation_Service`
   - Calculates monthly fees based on customer tier and balance
   - Replaces `CalculateMonthlyFees` stored procedure

3. **Rewards Calculation Service**
   - URL: `https://we5fvnijya.execute-api.us-west-2.amazonaws.com/default/Rewards_Calculation_Service`
   - Calculates monthly rewards based on account balance
   - Replaces `CalculateRewards` stored procedure

## Database Schema Migration

The migration transforms the monolithic schema into a normalized structure:

### Old Schema (BankingRewardsFees_Old)
- Single `Accounts` table containing customer and account data
- Stored calculated values (`monthly_fees`, `monthly_rewards`)
- Legacy stored procedures for calculations

### New Schema (BankingRewardsFees_New)
- Separated `Customers` and `Accounts` tables
- Foreign key relationships
- Real-time calculations (no stored values)
- Removed deprecated columns and procedures

## Getting Started

### Prerequisites
- Python 3.8+
- AWS Account (for Lambda deployment)
- MySQL database access
- Streamlit

### Installation

1. Clone the repository:
```bash
git clone https://github.com/frankoredey-codegpt/SP_to_Microservice.git
cd SP_to_Microservice
```

2. Install dependencies for the new application:
```bash
cd BankingRewardsFees_New
pip install -r requirements.txt
```

### Running the Legacy Application

```bash
cd BankingRewardsFees_Old
streamlit run app.py
```

### Running the Modern Application

1. Update the Lambda function URLs in `BankingRewardsFees_New/app.py` if needed:
```python
ACCOUNT_SERVICE_URL = "https://h4s7q404t9.execute-api.us-west-2.amazonaws.com/default/Account_Service"
FEE_CALCULATION_URL = "https://31ex1bcgtg.execute-api.us-west-2.amazonaws.com/default/Fee_Calculation_Service"
REWARDS_CALCULATION_URL = "https://we5fvnijya.execute-api.us-west-2.amazonaws.com/default/Rewards_Calculation_Service"
```

2. Run the application:
```bash
cd BankingRewardsFees_New
streamlit run app.py
```

## Migration Guide

The `Old_to_New_Migration/data_mapping.json` file provides detailed mapping for:
- Table structure changes (`Accounts` → `Customers` + `Accounts`)
- Column mappings (`customer_name` → `name`, `customer_tier` → `tier`)
- Deprecated elements (`monthly_fees`, `monthly_rewards` columns)
- Business logic migration from stored procedures to Python microservices

### Key Migration Points:
- Customer data separated from account data
- Stored procedures (`CalculateMonthlyFees`, `CalculateRewards`) converted to Python microservices
- Real-time calculations replace stored values
- Enhanced error handling and response formatting

## Features

### Legacy System Features:
- Account selection and viewing
- Monthly fee calculation via `CalculateMonthlyFees` stored procedure
- Monthly rewards calculation via `CalculateRewards` stored procedure
- Manual balance updates
- Direct database connections

### Modern System Features:
- Same UI/UX experience
- Microservices-based calculations
- RESTful API communication
- Cloud-native scalability
- Improved error handling with JSON response parsing
- Normalized data structure

## Technology Stack

### Legacy Stack:
- **Frontend**: Streamlit
- **Database**: MySQL with stored procedures
- **Connection**: Direct database connections
- **Host**: `database-2.crq7shsasjo0.us-west-2.rds.amazonaws.com`

### Modern Stack:
- **Frontend**: Streamlit 1.28.0
- **Backend**: AWS Lambda Functions
- **API**: RESTful services via API Gateway
- **Database**: MySQL (normalized schema)
- **Dependencies**: requests 2.31.0, pandas 2.1.0

## Development Notes

- The UI remains consistent between legacy and modern versions
- Business logic is preserved during migration from stored procedures to Python
- Error handling improved in microservices version with proper JSON response handling
- Database schema normalized for better data integrity
- Microservices enable independent scaling and deployment
- Session state management for calculated values in Streamlit

## API Integration

The modern application uses three main service calls:
- `call_account_service(action, **kwargs)` - Generic account operations
- `call_fee_calculation_service(account_id)` - Fee calculations
- `call_rewards_calculation_service(account_id)` - Rewards calculations

Each service handles different response formats and includes comprehensive error handling.

## Contributing

This repository serves as a demonstration of monolithic to microservices migration patterns. The codebase illustrates best practices for:
- Legacy system analysis and stored procedure migration
- Microservices decomposition
- Data schema evolution and normalization
- UI preservation during backend modernization
- AWS Lambda integration with Streamlit

## License

This project is for educational and demonstration purposes, showcasing enterprise application modernization patterns.

---

**Repository**: [frankoredey-codegpt/SP_to_Microservice](https://github.com/frankoredey-codegpt/SP_to_Microservice)" 
