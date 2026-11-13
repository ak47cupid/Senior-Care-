-- Adds a private random token used by the digital membership card QR code.
SET @has_member_qr_token = (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE() AND table_name = 'senior_citizens' AND column_name = 'member_qr_token'
);
SET @member_qr_sql = IF(@has_member_qr_token = 0,
  'ALTER TABLE senior_citizens ADD COLUMN member_qr_token CHAR(64) NULL UNIQUE',
  'SELECT 1'
);
PREPARE member_qr_stmt FROM @member_qr_sql;
EXECUTE member_qr_stmt;
DEALLOCATE PREPARE member_qr_stmt;
