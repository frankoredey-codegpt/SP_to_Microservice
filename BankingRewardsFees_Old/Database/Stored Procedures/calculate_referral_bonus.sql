DELIMITER $$
CREATE DEFINER=`admin`@`%` PROCEDURE `CalculateReferralBonus`(IN acc_id INT)
BEGIN
    -- Business no longer uses referral bonuses
    UPDATE Accounts
    SET monthly_rewards = monthly_rewards + 50
    WHERE account_id = acc_id;
END$$
DELIMITER ;