-- 调试 RENAME TABLE 问题
CREATE DATABASE test_db;
USE test_db;

-- 创建测试表
CREATE TABLE testrename (id int, name varchar(20));
SHOW TABLE testrename;

-- 列出当前文件（调试用）
\! ls -la *.tdata *.thead 2>/dev/null || echo "No table files found"

-- 尝试重命名
RENAME TABLE testrename TO renamedtable;

-- 检查是否成功
SHOW TABLE renamedtable;

-- 再次列出文件
\! ls -la *.tdata *.thead 2>/dev/null || echo "No table files found"

DROP TABLE renamed_table;
DROP DATABASE test_db;
EXIT;
