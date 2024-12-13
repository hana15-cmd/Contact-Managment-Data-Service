-- Drop users table if it exists
DROP TABLE IF EXISTS users;

-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT
);

-- Alter users table to add is_admin column
ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0;

-- Drop teams table if it exists
DROP TABLE IF EXISTS teams;

-- Create teams table if it doesn't exist
CREATE TABLE IF NOT EXISTS teams (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    TEAM_NAME TEXT NOT NULL,
    TEAM_LOCATION TEXT NOT NULL,
    NUMBER_OF_TEAM_MEMBERS INTEGER NOT NULL CHECK (NUMBER_OF_TEAM_MEMBERS > 0),
    EMAIL_ADDRESS TEXT NOT NULL UNIQUE
);

-- Drop contacts table if it exists
DROP TABLE IF EXISTS contacts;

-- Create contacts table
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT,
    email_address TEXT,
    phone_number TEXT,
    team_id INTEGER,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);
