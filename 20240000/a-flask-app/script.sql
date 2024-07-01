-- script.sql
CREATE DATABASE IF NOT EXISTS ufs05db;
USE ufs05db;
CREATE TABLE employees (
  first_name varchar(45) DEFAULT NULL,
  last_name varchar(45) DEFAULT NULL
);

INSERT INTO employees (first_name, last_name) VALUES ('marco', 'booo');