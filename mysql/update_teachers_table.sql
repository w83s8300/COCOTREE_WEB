-- 更新老師表格，移除 email 欄位的 UNIQUE 約束，允許電子郵件重複

-- 檢查 email 欄位是否有 UNIQUE 約束
SET @constraint_exists = 0;
SELECT COUNT(*) INTO @constraint_exists 
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu 
ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
WHERE tc.TABLE_SCHEMA = 'testdb' 
  AND tc.TABLE_NAME = 'teachers' 
  AND tc.CONSTRAINT_TYPE = 'UNIQUE'
  AND kcu.COLUMN_NAME = 'email';

-- 如果存在 UNIQUE 約束，則移除它
SET @sql = IF(@constraint_exists > 0, 
    'ALTER TABLE teachers DROP INDEX email',
    'SELECT ''Email UNIQUE constraint does not exist'' as message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 顯示約束移除結果
SELECT 
    CASE 
        WHEN @constraint_exists > 0 THEN 'Email UNIQUE constraint has been removed successfully'
        ELSE 'Email UNIQUE constraint was not found'
    END as result;

-- 顯示更新後的表格結構
DESCRIBE teachers;

-- 顯示老師表格的所有索引
SHOW INDEX FROM teachers;
