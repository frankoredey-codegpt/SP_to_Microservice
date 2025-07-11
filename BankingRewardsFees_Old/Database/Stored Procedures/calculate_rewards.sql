DELIMITER $$
CREATE DEFINER=`admin`@`%` PROCEDURE `CalculateRewards`(IN acc_id INT)
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
END$$
DELIMITER ;