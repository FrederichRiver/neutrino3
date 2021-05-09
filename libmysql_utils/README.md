#### 建立数据库
```
CREATE database_name
```
#### 查看表如何创建
```
SHOW CREATE TABLE table_name
```
#### 查看表的定义
```
SHOW FULL FIELDS FROM TABLE tablename
```
#### 建立表
```
CREATE TABLE table_name (
    `col_1` date NOT NULL,
    `col_2` varchar(20) DEFAULT NULL,
    PRIMARY KEY(`col_1`) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8
```
#### 查询数据
```
SELECT column_name FROM table_name WHERE condition 
```
#### 联合查询
```
SELECT col_1 FROM table_1 WHERE cond1
UNION
SELECT col_2 FROM table_2 WHERE cond2
```