-- MySQL User Setup Script for OpenTickets Database
-- This script creates three database users with specific permission levels

-- 1. HEALTHCHECK USER - Status monitoring and server control
CREATE USER IF NOT EXISTS 'healthcheck'@'localhost' IDENTIFIED BY 'AAAAC3NzaC1lZDI1NTE5AAAAIAmMoa0Z/oe52h0qPZqhtmk6rtzP7kVKn1HB7TUxOTFp';
GRANT SELECT ON opentickets_db.* TO 'healthcheck'@'localhost';
GRANT PROCESS, REPLICATION CLIENT, SHOW DATABASES, SHOW VIEW ON *.* TO 'healthcheck'@'localhost';
GRANT SUPER ON *.* TO 'healthcheck'@'localhost';
FLUSH PRIVILEGES;

-- 2. DATABASE USER - Full write/read permissions for the application
CREATE USER IF NOT EXISTS 'dbuser'@'%' IDENTIFIED BY 'AAAAC3NzaC1lZDI1NTE5AAAAIP/n3+/IYfe8G7OcTUMqSRpzZ5MO2mRXcDtioHqFBG6Z';
GRANT SELECT, INSERT, UPDATE, DELETE ON opentickets_db.* TO 'dbuser'@'%';
GRANT CREATE TEMPORARY TABLES ON opentickets_db.* TO 'dbuser'@'%';
FLUSH PRIVILEGES;

-- 3. ROOT USER - Restricted to localhost only
-- Drop the old unrestricted root user
DROP USER IF EXISTS 'root'@'%';
DROP USER IF EXISTS 'root'@'::1';

-- Create root user for localhost only with strong key-based auth
ALTER USER 'root'@'localhost' IDENTIFIED BY 'AAAAC3NzaC1lZDI1NTE5AAAAIOdU9kBv81VySttnQMjA3oeerpm0f07p7VUdHZ12xwZ5';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- Verify the users
SELECT User, Host FROM mysql.user WHERE User IN ('healthcheck', 'dbuser', 'root');
