CREATE TABLE `Accounts` (
  `account_id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(255) DEFAULT NULL,
  `customer_tier` varchar(50) DEFAULT NULL,
  `balance` decimal(15,2) DEFAULT NULL,
  `monthly_fees` decimal(10,2) DEFAULT NULL,
  `monthly_rewards` decimal(10,2) DEFAULT NULL,
  `legacy_flag` char(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;