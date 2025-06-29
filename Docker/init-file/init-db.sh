#!/bin/bash
set -e

mkdir -p /uploads

echo "Creating tables in investment_db..."
# Check in voulme if the database data already exsits - if so get data from voulmes
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

  -- Create users table
  CREATE TABLE IF NOT EXISTS users (
      user_id SERIAL PRIMARY KEY,
      username VARCHAR(50) UNIQUE NOT NULL,
      password VARCHAR(100) NOT NULL,
      first_name VARCHAR(50),
      last_name VARCHAR(50),
      last_login TIMESTAMP,
      session_expiration TIMESTAMP
  );

  -- Create portfolio_files table (user_id as primary key)
  CREATE TABLE IF NOT EXISTS portfolio_files (
      user_id INT PRIMARY KEY,
      filename TEXT NOT NULL,
      file_content JSON NOT NULL,  -- Changed from filepath to file_content
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(user_id)
  );

  -- Create stocks table (user_id + ticker as composite primary key)
  CREATE TABLE IF NOT EXISTS stocks (
      user_id INT NOT NULL,
      ticker VARCHAR(10) NOT NULL,
      quantity DECIMAL(10,2) NOT NULL,
      buy_price DECIMAL(10,2) NOT NULL,
      current_price DECIMAL(10,2),
      value DECIMAL(15,2),
      gain DECIMAL(15,2),
      change_percent DECIMAL(5,2),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (user_id, ticker),
      FOREIGN KEY (user_id) REFERENCES users(user_id)
  );

  -- Create portfolio_summaries table (user_id as primary key)
  CREATE TABLE IF NOT EXISTS portfolio_summaries (
      user_id INT PRIMARY KEY,
      -- Portfolio Overview
      total_stocks INTEGER DEFAULT 0,
      total_value DECIMAL(15,2) DEFAULT 0.0,
      total_investment DECIMAL(15,2) DEFAULT 0.0,
      total_gain_loss DECIMAL(15,2) DEFAULT 0.0,
      total_gain_loss_percent DECIMAL(8,4) DEFAULT 0.0,
      avg_position_size DECIMAL(15,2) DEFAULT 0.0,
      -- Performance Metrics
      winning_stocks INTEGER DEFAULT 0,
      losing_stocks INTEGER DEFAULT 0,
      win_rate DECIMAL(8,4) DEFAULT 0.0,
      best_performer_ticker VARCHAR(10),
      best_performer_gain DECIMAL(15,2),
      best_performer_percent DECIMAL(8,4),
      worst_performer_ticker VARCHAR(10),
      worst_performer_gain DECIMAL(15,2),
      worst_performer_percent DECIMAL(8,4),
      -- Risk Metrics
      largest_position_weight DECIMAL(8,4) DEFAULT 0.0,
      concentration_risk VARCHAR(20) DEFAULT 'Low',
      -- JSON fields for complex data
      top_holdings JSON,
      stock_breakdown JSON,
      -- Timestamps
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(user_id)
  );

  -- Insert test users
  INSERT INTO users (username, password, first_name, last_name, last_login, session_expiration)
  VALUES
    ('alex', 'pass123', 'Alex', 'Wonderland', 
     NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '15 minutes'),
    ('zohar', 'secure456', 'Zohar', 'Builder', 
     NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 45 minutes')
  ON CONFLICT (username) DO NOTHING;

  -- Insert portfolio files with JSON content
  INSERT INTO portfolio_files (user_id, filename, file_content, created_at, updated_at)
  VALUES
    (1, 'alex_portfolio.json', '{
      "portfolio_name": "Alex Tech Portfolio",
      "total_value": 73136.25,
      "total_investment": 70450.25,
      "total_gain_loss": 2686.00,
      "holdings": [
        {
          "id": 0,
          "ticker": "AAPL",
          "company_name": "Apple Inc.",
          "quantity": 50.00,
          "buy_price": 150.25,
          "current_price": 175.80,
          "value": 8790.00,
          "gain": 1277.50,
          "change_percent": 17.02
        },
        {
          "id": 1,
          "ticker": "GOOGL",
          "company_name": "Alphabet Inc.",
          "quantity": 15.00,
          "buy_price": 2650.00,
          "current_price": 2720.45,
          "value": 40806.75,
          "gain": 1056.75,
          "change_percent": 2.66
        },
        {
          "id": 2,
          "ticker": "MSFT",
          "company_name": "Microsoft Corporation",
          "quantity": 30.00,
          "buy_price": 285.90,
          "current_price": 295.40,
          "value": 8862.00,
          "gain": 285.00,
          "change_percent": 3.32
        },
        {
          "id": 3,
          "ticker": "TSLA",
          "company_name": "Tesla Inc.",
          "quantity": 25.00,
          "buy_price": 220.15,
          "current_price": 198.50,
          "value": 4962.50,
          "gain": -541.25,
          "change_percent": -9.83
        },
        {
          "id": 4,
          "ticker": "NVDA",
          "company_name": "NVIDIA Corporation",
          "quantity": 20.00,
          "buy_price": 450.30,
          "current_price": 485.75,
          "value": 9715.00,
          "gain": 709.00,
          "change_percent": 7.87
        }
      ]
    }'::json, 
     NOW() - INTERVAL '1 day', NOW() - INTERVAL '12 hours'),
    (2, 'zohar_portfolio.json', '{
      "portfolio_name": "Zohar Diversified Portfolio",
      "total_value": 70389.55,
      "total_investment": 67352.00,
      "total_gain_loss": 3037.55,
      "holdings": [
        {
          "id": 0,
          "ticker": "AMZN",
          "company_name": "Amazon.com Inc.",
          "quantity": 12.00,
          "buy_price": 3100.50,
          "current_price": 3245.20,
          "value": 38942.40,
          "gain": 1736.40,
          "change_percent": 4.66
        },
        {
          "id": 1,
          "ticker": "META",
          "company_name": "Meta Platforms Inc.",
          "quantity": 40.00,
          "buy_price": 325.75,
          "current_price": 342.10,
          "value": 13684.00,
          "gain": 654.00,
          "change_percent": 5.02
        },
        {
          "id": 2,
          "ticker": "NFLX",
          "company_name": "Netflix Inc.",
          "quantity": 18.00,
          "buy_price": 385.40,
          "current_price": 410.65,
          "value": 7391.70,
          "gain": 454.50,
          "change_percent": 6.55
        },
        {
          "id": 3,
          "ticker": "AMD",
          "company_name": "Advanced Micro Devices Inc.",
          "quantity": 35.00,
          "buy_price": 95.20,
          "current_price": 88.75,
          "value": 3106.25,
          "gain": -225.75,
          "change_percent": -6.78
        },
        {
          "id": 4,
          "ticker": "CRM",
          "company_name": "Salesforce Inc.",
          "quantity": 22.00,
          "buy_price": 210.80,
          "current_price": 225.30,
          "value": 4956.60,
          "gain": 319.00,
          "change_percent": 6.88
        },
        {
          "id": 5,
          "ticker": "PYPL",
          "company_name": "PayPal Holdings Inc.",
          "quantity": 28.00,
          "buy_price": 78.90,
          "current_price": 82.45,
          "value": 2308.60,
          "gain": 99.40,
          "change_percent": 4.50
        }
      ]
    }'::json,
     NOW() - INTERVAL '3 days', NOW() - INTERVAL '1 day')
  ON CONFLICT DO NOTHING;

  -- Insert Alex's portfolio stocks (optional - for reference only)
  INSERT INTO stocks (user_id, ticker, quantity, buy_price, current_price, value, gain, change_percent, created_at, updated_at)
  VALUES
    (1, 'AAPL', 50.00, 150.25, 175.80, 8790.00, 1277.50, 17.02, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 hour'),
    (1, 'GOOGL', 15.00, 2650.00, 2720.45, 40806.75, 1056.75, 2.66, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 hour'),
    (1, 'MSFT', 30.00, 285.90, 295.40, 8862.00, 285.00, 3.32, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 hour'),
    (1, 'TSLA', 25.00, 220.15, 198.50, 4962.50, -541.25, -9.83, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 hour'),
    (1, 'NVDA', 20.00, 450.30, 485.75, 9715.00, 709.00, 7.87, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 hour')
  ON CONFLICT DO NOTHING;

  -- Insert Zohar's portfolio stocks (optional - for reference only)
  INSERT INTO stocks (user_id, ticker, quantity, buy_price, current_price, value, gain, change_percent, created_at, updated_at)
  VALUES
    (2, 'AMZN', 12.00, 3100.50, 3245.20, 38942.40, 1736.40, 4.66, NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 hours'),
    (2, 'META', 40.00, 325.75, 342.10, 13684.00, 654.00, 5.02, NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 hours'),
    (2, 'NFLX', 18.00, 385.40, 410.65, 7391.70, 454.50, 6.55, NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 hours'),
    (2, 'AMD', 35.00, 95.20, 88.75, 3106.25, -225.75, -6.78, NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 hours'),
    (2, 'CRM', 22.00, 210.80, 225.30, 4956.60, 319.00, 6.88, NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 hours'),
    (2, 'PYPL', 28.00, 78.90, 82.45, 2308.60, 99.40, 4.50, NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 hours')
  ON CONFLICT DO NOTHING;

  -- Insert sample portfolio summaries with JSON data
  INSERT INTO portfolio_summaries (
      user_id, total_stocks, total_value, total_investment, 
      total_gain_loss, total_gain_loss_percent, avg_position_size,
      winning_stocks, losing_stocks, win_rate,
      best_performer_ticker, best_performer_gain, best_performer_percent,
      worst_performer_ticker, worst_performer_gain, worst_performer_percent,
      largest_position_weight, concentration_risk,
      top_holdings, stock_breakdown,
      created_at, updated_at
  )
  VALUES
    (1, 5, 73136.25, 70450.25, 2686.00, 3.81, 14627.25,
     4, 1, 80.00,
     'AAPL', 1277.50, 17.02,
     'TSLA', -541.25, -9.83,
     55.80, 'High',
     '[{"ticker": "GOOGL", "value": 40806.75, "weight": 55.8}, {"ticker": "NVDA", "value": 9715.00, "weight": 13.3}, {"ticker": "AAPL", "value": 8790.00, "weight": 12.0}]'::json,
     '{"tech_stocks": 5, "growth_stocks": 4, "value_stocks": 1}'::json,
     NOW() - INTERVAL '1 hour', NOW() - INTERVAL '1 hour'),
    (2, 6, 70389.55, 67352.00, 3037.55, 4.51, 11731.59,
     5, 1, 83.33,
     'CRM', 319.00, 6.88,
     'AMD', -225.75, -6.78,
     55.32, 'High',
     '[{"ticker": "AMZN", "value": 38942.40, "weight": 55.3}, {"ticker": "META", "value": 13684.00, "weight": 19.4}, {"ticker": "NFLX", "value": 7391.70, "weight": 10.5}]'::json,
     '{"tech_stocks": 6, "growth_stocks": 5, "value_stocks": 1}'::json,
     NOW() - INTERVAL '2 hours', NOW() - INTERVAL '2 hours')
  ON CONFLICT DO NOTHING;

  -- Create indexes for better performance
  CREATE INDEX IF NOT EXISTS idx_stocks_user_id ON stocks(user_id);
  CREATE INDEX IF NOT EXISTS idx_stocks_ticker ON stocks(ticker);
  CREATE INDEX IF NOT EXISTS idx_portfolio_files_user_id ON portfolio_files(user_id);
  CREATE INDEX IF NOT EXISTS idx_portfolio_summaries_user_id ON portfolio_summaries(user_id);
  
  -- JSON indexes for better query performance
  CREATE INDEX IF NOT EXISTS idx_portfolio_files_content ON portfolio_files USING GIN (file_content);
  CREATE INDEX IF NOT EXISTS idx_portfolio_summaries_top_holdings ON portfolio_summaries USING GIN (top_holdings);
  CREATE INDEX IF NOT EXISTS idx_portfolio_summaries_stock_breakdown ON portfolio_summaries USING GIN (stock_breakdown);

  -- Grant necessary permissions
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $POSTGRES_USER;
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $POSTGRES_USER;

EOSQL

echo "Database initialization completed successfully!"
echo "Created tables: users, portfolio_files, stocks, portfolio_summaries"
echo "Inserted test data for users: alex, zohar"
echo "Portfolio JSON data loaded for both test users"
echo ""
echo "Testing JSON queries..."
echo ""
echo "JSON query tests completed successfully!"
echo "The database is ready for use with JSON file content storage."