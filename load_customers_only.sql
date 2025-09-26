-- Load customers, accounts, and transactions only (branches already exist)

-- Generate customers with diverse profiles
INSERT INTO customers (first_name, last_name, email, phone, date_of_birth, ssn, address, city, state, zip_code, employment_status, annual_income, credit_score, customer_segment, risk_category, kyc_status, branch_id)
SELECT
    CASE (random()*20)::INT
        WHEN 0 THEN 'James' WHEN 1 THEN 'Mary' WHEN 2 THEN 'John' WHEN 3 THEN 'Patricia'
        WHEN 4 THEN 'Robert' WHEN 5 THEN 'Jennifer' WHEN 6 THEN 'Michael' WHEN 7 THEN 'Linda'
        WHEN 8 THEN 'William' WHEN 9 THEN 'Elizabeth' WHEN 10 THEN 'David' WHEN 11 THEN 'Barbara'
        WHEN 12 THEN 'Richard' WHEN 13 THEN 'Susan' WHEN 14 THEN 'Joseph' WHEN 15 THEN 'Jessica'
        WHEN 16 THEN 'Thomas' WHEN 17 THEN 'Sarah' WHEN 18 THEN 'Christopher' ELSE 'Karen'
    END AS first_name,
    CASE (random()*20)::INT
        WHEN 0 THEN 'Smith' WHEN 1 THEN 'Johnson' WHEN 2 THEN 'Williams' WHEN 3 THEN 'Brown'
        WHEN 4 THEN 'Jones' WHEN 5 THEN 'Garcia' WHEN 6 THEN 'Miller' WHEN 7 THEN 'Davis'
        WHEN 8 THEN 'Rodriguez' WHEN 9 THEN 'Martinez' WHEN 10 THEN 'Hernandez' WHEN 11 THEN 'Lopez'
        WHEN 12 THEN 'Gonzalez' WHEN 13 THEN 'Wilson' WHEN 14 THEN 'Anderson' WHEN 15 THEN 'Thomas'
        WHEN 16 THEN 'Taylor' WHEN 17 THEN 'Moore' WHEN 18 THEN 'Jackson' ELSE 'Martin'
    END AS last_name,
    'user' || s.n || '@email.com' AS email,
    '(' || (200 + (random()*800)::INT) || ') ' || (200 + (random()*700)::INT) || '-' || (1000 + (random()*9000)::INT) AS phone,
    (current_date - interval '18 years' - (random() * interval '50 years'))::date AS date_of_birth,
    -- Generate valid SSN format within VARCHAR(20) limit
    LPAD((100 + (random()*899)::INT)::text, 3, '0') || '-' ||
    LPAD((10 + (random()*89)::INT)::text, 2, '0') || '-' ||
    LPAD((1000 + (random()*8999)::INT)::text, 4, '0') AS ssn,
    (100 + s.n) || ' Main Street' AS address,
    CASE (random()*10)::INT
        WHEN 0 THEN 'New York' WHEN 1 THEN 'Los Angeles' WHEN 2 THEN 'Chicago'
        WHEN 3 THEN 'Houston' WHEN 4 THEN 'Phoenix' WHEN 5 THEN 'Philadelphia'
        WHEN 6 THEN 'San Antonio' WHEN 7 THEN 'San Diego' WHEN 8 THEN 'Dallas'
        ELSE 'Austin'
    END AS city,
    CASE (random()*10)::INT
        WHEN 0 THEN 'NY' WHEN 1 THEN 'CA' WHEN 2 THEN 'IL'
        WHEN 3 THEN 'TX' WHEN 4 THEN 'AZ' WHEN 5 THEN 'PA'
        WHEN 6 THEN 'TX' WHEN 7 THEN 'CA' WHEN 8 THEN 'TX'
        ELSE 'TX'
    END AS state,
    LPAD((10000 + (random()*89999)::INT)::text, 5, '0') AS zip_code,
    CASE (random()*5)::INT
        WHEN 0 THEN 'employed' WHEN 1 THEN 'employed' WHEN 2 THEN 'employed'
        WHEN 3 THEN 'self_employed' ELSE 'retired'
    END AS employment_status,
    (25000 + random() * 275000)::numeric(12,2) AS annual_income,
    (300 + random() * 550)::INT AS credit_score,
    CASE
        WHEN random() < 0.1 THEN 'private_banking'
        WHEN random() < 0.3 THEN 'premium'
        WHEN random() < 0.8 THEN 'retail'
        ELSE 'business'
    END AS customer_segment,
    CASE
        WHEN random() < 0.6 THEN 'low'
        WHEN random() < 0.9 THEN 'medium'
        ELSE 'high'
    END AS risk_category,
    CASE
        WHEN random() < 0.9 THEN 'approved'
        WHEN random() < 0.95 THEN 'under_review'
        ELSE 'pending'
    END AS kyc_status,
    (1 + (random() * 24)::INT) AS branch_id
FROM generate_series(1, 100) AS s(n);

-- Generate accounts for customers (1-3 accounts per customer)
INSERT INTO accounts (customer_id, account_number, account_type, balance, interest_rate, minimum_balance, account_status, overdraft_limit, branch_id, opened_date)
SELECT
    c.customer_id,
    '10' || LPAD(c.customer_id::text, 6, '0') || LPAD(account_seq.n::text, 2, '0') AS account_number,
    CASE account_seq.n
        WHEN 1 THEN 'checking'
        WHEN 2 THEN 'savings'
        ELSE 'money_market'
    END AS account_type,
    CASE account_seq.n
        WHEN 1 THEN (500 + random() * 49500)::numeric(15,2)  -- Checking: $500-$50k
        WHEN 2 THEN (1000 + random() * 199000)::numeric(15,2)  -- Savings: $1k-$200k
        ELSE (5000 + random() * 495000)::numeric(15,2)  -- Money Market: $5k-$500k
    END AS balance,
    CASE account_seq.n
        WHEN 1 THEN 0.0100
        WHEN 2 THEN 0.0250
        ELSE 0.0375
    END AS interest_rate,
    CASE account_seq.n
        WHEN 1 THEN 100.00
        WHEN 2 THEN 100.00
        ELSE 2500.00
    END AS minimum_balance,
    'active' AS account_status,
    CASE account_seq.n
        WHEN 1 THEN (500 + random() * 4500)::numeric(10,2)
        ELSE 0.00
    END AS overdraft_limit,
    c.branch_id,
    (current_date - interval '5 years' + (random() * interval '4 years'))::date AS opened_date
FROM customers c
CROSS JOIN generate_series(1, 2) AS account_seq(n)  -- Each customer gets 2 accounts
WHERE c.customer_id <= 100;

-- Generate recent transactions (last 30 days)
INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, transaction_date, merchant_name, merchant_category, location, channel, reference_number, status)
SELECT
    a.account_id,
    CASE (random()*6)::INT
        WHEN 0 THEN 'deposit' WHEN 1 THEN 'withdrawal' WHEN 2 THEN 'transfer_in'
        WHEN 3 THEN 'transfer_out' WHEN 4 THEN 'fee' ELSE 'online'
    END AS transaction_type,
    CASE
        WHEN (random()*6)::INT = 0 THEN (50 + random() * 4950)::numeric(12,2)  -- Deposits
        ELSE (10 + random() * 490)::numeric(12,2)  -- Withdrawals/transfers
    END AS amount,
    a.balance AS balance_after,  -- Simplified - just use current balance
    CASE (random()*5)::INT
        WHEN 0 THEN 'Salary deposit' WHEN 1 THEN 'ATM withdrawal' WHEN 2 THEN 'Online purchase'
        WHEN 3 THEN 'Transfer payment' ELSE 'Service fee'
    END AS description,
    (current_date - (random() * 30)::INT * interval '1 day')::timestamp AS transaction_date,
    CASE (random()*8)::INT
        WHEN 0 THEN 'Amazon' WHEN 1 THEN 'Starbucks' WHEN 2 THEN 'Shell'
        WHEN 3 THEN 'Walmart' WHEN 4 THEN 'Target' WHEN 5 THEN 'McDonald''s'
        WHEN 6 THEN 'Apple Store' ELSE 'Home Depot'
    END AS merchant_name,
    CASE (random()*6)::INT
        WHEN 0 THEN 'Retail' WHEN 1 THEN 'Food & Beverage' WHEN 2 THEN 'Gas Station'
        WHEN 3 THEN 'Grocery' WHEN 4 THEN 'Electronics' ELSE 'Home Improvement'
    END AS merchant_category,
    'New York, NY' AS location,
    CASE (random()*4)::INT
        WHEN 0 THEN 'online' WHEN 1 THEN 'mobile' WHEN 2 THEN 'atm' ELSE 'branch'
    END AS channel,
    'TXN' || LPAD((1000 + random() * 8999)::INT::text, 4, '0') AS reference_number,
    'completed' AS status
FROM accounts a
CROSS JOIN generate_series(1, 5) AS txn_seq(n)  -- 5 transactions per account
WHERE a.account_id <= 200;