-- Smart Medicine Reminder and Inventory System
-- Database Schema

CREATE DATABASE IF NOT EXISTS smartmedicine;
USE smartmedicine;

-- -----------------------------------------------------
-- Table: users
-- -----------------------------------------------------

CREATE TABLE users (
    email VARCHAR(255) PRIMARY KEY,
    family_email VARCHAR(255),
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- -----------------------------------------------------
-- Table: medicines
-- -----------------------------------------------------

CREATE TABLE medicines (
    id VARCHAR(20) PRIMARY KEY,
    user_email VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100),
    time TIME,
    quantity INT,
    expiry_date DATE,
    last_taken DATE,
    status ENUM('Pending','Taken','Missed') DEFAULT 'Pending',
    reminder_sent BOOLEAN DEFAULT FALSE,
    low_stock_sent BOOLEAN DEFAULT FALSE,
    expiry_sent BOOLEAN DEFAULT FALSE,
    missed_sent BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (user_email)
        REFERENCES users(email)
        ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Table: dose_logs
-- -----------------------------------------------------

CREATE TABLE dose_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255),
    medicine_id VARCHAR(20),
    date_taken DATE,

    FOREIGN KEY (user_email)
        REFERENCES users(email)
        ON DELETE CASCADE,

    FOREIGN KEY (medicine_id)
        REFERENCES medicines(id)
        ON DELETE CASCADE
);
