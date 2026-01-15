-- 测试ALTER TABLE和RENAME TABLE功能
CREATE DATABASE test_db;
USE test_db;

-- 创建测试表
CREATE TABLE test_table (
    id int PRIMARY KEY,
    name varchar(20),
    age int
);

-- 显示表结构
SHOW TABLE test_table;

-- 重命名表
RENAME TABLE test_table TO renamed_table;

-- 显示重命名后的表
SHOW TABLE renamed_table;

-- 添加新列
ALTER TABLE renamed_table ADD COLUMN email varchar(30);

-- 删除列  
ALTER TABLE renamed_table DROP COLUMN age;

-- 修改列
ALTER TABLE renamed_table MODIFY COLUMN name varchar(50);

-- 显示最终表结构
SHOW TABLE renamed_table;

EXIT;