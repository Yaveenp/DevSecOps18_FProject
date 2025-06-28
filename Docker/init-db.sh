
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
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(user_id)
  );

  INSERT INTO users (username, password, first_name, last_name, last_login, session_expiration)
  VALUES
    ('alex', 'pass123', 'Alex', 'Wonderland', 
     NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '15 minutes'),
    ('zoher', 'secure456', 'Zoher', 'Builder', 
     NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 45 minutes')
  ON CONFLICT (username) DO NOTHING;

  INSERT INTO portfolio_files (user_id, filename, filepath, created_at, updated_at)
  VALUES
    (1, 'alex_portfolio.csv', '/uploads/alex_portfolio.csv', 
     NOW() - INTERVAL '1 day', NOW() - INTERVAL '12 hours'),
    (2, 'zoher_investments.xlsx', '/uploads/zoher_investments.xlsx',
     NOW() - INTERVAL '3 days', NOW() - INTERVAL '1 day')
  ON CONFLICT DO NOTHING;

EOSQL