-- File: customers_table.sql
CREATE TABLE Customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(255),
    tier VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME
);