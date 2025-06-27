#!/bin/bash
set -e

echo "Creating tables in investment_db..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

  CREATE TABLE IF NOT EXISTS users (
      user_id SERIAL PRIMARY KEY,
      username VARCHAR(50) UNIQUE NOT NULL,
      password VARCHAR(100) NOT NULL,
      first_name VARCHAR(50),
      last_name VARCHAR(50),
      last_login TIMESTAMP,
      session_expiration TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS portfolio_files (
      id SERIAL PRIMARY KEY,
      user_id INT NOT NULL,
      filename TEXT NOT NULL,
      filepath TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(user_id)
  );

  CREATE TABLE IF NOT EXISTS investments (
      id SERIAL PRIMARY KEY,
      user_id INT NOT NULL,
      ticker VARCHAR(20) NOT NULL,
      quantity INTEGER NOT NULL,
      buy_price NUMERIC(10, 2) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(user_id)
  );

  INSERT INTO users (username, password, first_name, last_name, last_login, session_expiration)
  VALUES
    ('alice', 'pass123', 'Alice', 'Wonderland', 
     NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '15 minutes'),
    ('bob', 'secure456', 'Bob', 'Builder', 
     NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 45 minutes')
  ON CONFLICT (username) DO NOTHING;