-- File: accounts_table.sql
CREATE TABLE Accounts (
    account_id INT PRIMARY KEY,
    customer_id INT,
    balance DECIMAL(10,2),
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);