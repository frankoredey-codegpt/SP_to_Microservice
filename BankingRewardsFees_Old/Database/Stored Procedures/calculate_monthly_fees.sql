DELIMITER $$
CREATE DEFINER=`admin`@`%` PROCEDURE `CalculateMonthlyFees`(IN acc_id INT)
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
END$$
DELIMITER ;