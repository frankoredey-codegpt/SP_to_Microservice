DELIMITER $$
CREATE DEFINER=`admin`@`%` PROCEDURE `LegacyAccountCleanup`()
BEGIN
    -- This used to clean up legacy_flag, but no longer called anywhere
    UPDATE Accounts
    SET legacy_flag = 'N'
    WHERE legacy_flag = 'Y';
END$$
DELIMITER ;