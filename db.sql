CREATE DATABASE studentsdb;
USE studentsdb;

CREATE TABLE STUDENTS (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(50) NOT NULL, 
    email VARCHAR(70) NOT NULL, 
    phone VARCHAR(20) NOT NULL, 
    course VARCHAR(100), 
    address TEXT, 
    contact VARCHAR(20)
);