-- Banking Data Generation Script
-- Creates 1000+ customers with realistic banking scenarios for presentations

-- Insert Branches (25 branches across major cities)
INSERT INTO branches (branch_name, branch_code, address, city, state, zip_code, phone) VALUES
('Downtown Manhattan', 'NYC001', '123 Wall Street', 'New York', 'NY', '10005', '212-555-0001'),
('Midtown Plaza', 'NYC002', '456 5th Avenue', 'New York', 'NY', '10018', '212-555-0002'),
('Brooklyn Heights', 'NYC003', '789 Brooklyn Bridge Blvd', 'Brooklyn', 'NY', '11201', '718-555-0003'),
('Los Angeles Main', 'LAX001', '321 Wilshire Blvd', 'Los Angeles', 'CA', '90010', '213-555-0004'),
('Beverly Hills', 'LAX002', '654 Rodeo Drive', 'Beverly Hills', 'CA', '90210', '310-555-0005'),
('Chicago Loop', 'CHI001', '987 State Street', 'Chicago', 'IL', '60602', '312-555-0006'),
('Lincoln Park', 'CHI002', '147 North Ave', 'Chicago', 'IL', '60614', '312-555-0007'),
('Houston Center', 'HOU001', '258 Main Street', 'Houston', 'TX', '77002', '713-555-0008'),
('River Oaks', 'HOU002', '369 River Oaks Blvd', 'Houston', 'TX', '77019', '713-555-0009'),
('Phoenix Downtown', 'PHX001', '741 Central Ave', 'Phoenix', 'AZ', '85004', '602-555-0010'),
('Scottsdale', 'PHX002', '852 Scottsdale Rd', 'Scottsdale', 'AZ', '85251', '480-555-0011'),
('Philadelphia Center', 'PHL001', '963 Market Street', 'Philadelphia', 'PA', '19107', '215-555-0012'),
('San Antonio Plaza', 'SAT001', '159 Commerce Street', 'San Antonio', 'TX', '78205', '210-555-0013'),
('San Diego Bay', 'SAN001', '357 Harbor Drive', 'San Diego', 'CA', '92101', '619-555-0014'),
('Dallas Financial', 'DFW001', '468 Main Street', 'Dallas', 'TX', '75202', '214-555-0015'),
('San Jose Tech', 'SJC001', '579 Technology Way', 'San Jose', 'CA', '95110', '408-555-0016'),
('Austin Downtown', 'AUS001', '681 Congress Ave', 'Austin', 'TX', '78701', '512-555-0017'),
('Jacksonville Beach', 'JAX001', '792 Beach Blvd', 'Jacksonville', 'FL', '32250', '904-555-0018'),
('Fort Worth Plaza', 'FTW001', '813 Main Street', 'Fort Worth', 'TX', '76102', '817-555-0019'),
('Columbus Circle', 'CMH001', '924 High Street', 'Columbus', 'OH', '43215', '614-555-0020'),
('Charlotte Uptown', 'CLT001', '135 Tryon Street', 'Charlotte', 'NC', '28202', '704-555-0021'),
('Seattle Downtown', 'SEA001', '246 Pike Street', 'Seattle', 'WA', '98101', '206-555-0022'),
('Denver Tech', 'DEN001', '357 17th Street', 'Denver', 'CO', '80202', '303-555-0023'),
('Washington Metro', 'DCA001', '468 K Street NW', 'Washington', 'DC', '20001', '202-555-0024'),
('Boston Financial', 'BOS001', '579 State Street', 'Boston', 'MA', '02109', '617-555-0025');

-- Generate 1200 customers with diverse profiles
INSERT INTO customers (first_name, last_name, email, phone, date_of_birth, ssn, address, city, state, zip_code, employment_status, annual_income, credit_score, customer_segment, risk_category, kyc_status, branch_id)
SELECT 
    CASE (random()*20)::INT
        WHEN 0 THEN 'James' WHEN 1 THEN 'Mary' WHEN 2 THEN 'John' WHEN 3 THEN 'Patricia'
        WHEN 4 THEN 'Robert' WHEN 5 THEN 'Jennifer' WHEN 6 THEN 'Michael' WHEN 7 THEN 'Linda'
        WHEN 8 THEN 'William' WHEN 9 THEN 'Elizabeth' WHEN 10 THEN 'David' WHEN 11 THEN 'Barbara'
        WHEN 12 THEN 'Richard' WHEN 13 THEN 'Susan' WHEN 14 THEN 'Joseph' WHEN 15 THEN 'Jessica'
        WHEN 16 THEN 'Thomas' WHEN 17 THEN 'Sarah' WHEN 18 THEN 'Christopher' ELSE 'Karen'
    END || ' ' || s.n AS first_name,
    CASE (random()*20)::INT
        WHEN 0 THEN 'Smith' WHEN 1 THEN 'Johnson' WHEN 2 THEN 'Williams' WHEN 3 THEN 'Brown'
        WHEN 4 THEN 'Jones' WHEN 5 THEN 'Garcia' WHEN 6 THEN 'Miller' WHEN 7 THEN 'Davis'
        WHEN 8 THEN 'Rodriguez' WHEN 9 THEN 'Martinez' WHEN 10 THEN 'Hernandez' WHEN 11 THEN 'Lopez'
        WHEN 12 THEN 'Gonzalez' WHEN 13 THEN 'Wilson' WHEN 14 THEN 'Anderson' WHEN 15 THEN 'Thomas'
        WHEN 16 THEN 'Taylor' WHEN 17 THEN 'Moore' WHEN 18 THEN 'Jackson' ELSE 'Martin'
    END AS last_name,
    'user' || s.n || '@email.com' AS email,
    '(' || (200 + (random()*800)::INT) || ') ' || (200 + (random()*700)::INT) || '-' || (1000 + (random()*9000)::INT) AS phone,
    DATE '1950-01-01' + (random() * (DATE '2000-01-01' - DATE '1950-01-01'))::INT AS date_of_birth,
    LPAD((100000000 + (random()*899999999)::BIGINT)::TEXT, 9, '0') || '-' || LPAD((10 + (random()*89)::INT)::TEXT, 2, '0') AS ssn,
    (100 + (random()*9900)::INT) || ' ' || 
    CASE (random()*10)::INT
        WHEN 0 THEN 'Main St' WHEN 1 THEN 'Oak Ave' WHEN 2 THEN 'First St' WHEN 3 THEN 'Second Ave'
        WHEN 4 THEN 'Park Blvd' WHEN 5 THEN 'Center St' WHEN 6 THEN 'Elm Ave' WHEN 7 THEN 'Maple St'
        WHEN 8 THEN 'Washington Ave' ELSE 'Lincoln Blvd'
    END AS address,
    CASE (random()*10)::INT
        WHEN 0 THEN 'New York' WHEN 1 THEN 'Los Angeles' WHEN 2 THEN 'Chicago' WHEN 3 THEN 'Houston'
        WHEN 4 THEN 'Phoenix' WHEN 5 THEN 'Philadelphia' WHEN 6 THEN 'San Antonio' WHEN 7 THEN 'San Diego'
        WHEN 8 THEN 'Dallas' ELSE 'San Jose'
    END AS city,
    CASE (random()*10)::INT
        WHEN 0 THEN 'NY' WHEN 1 THEN 'CA' WHEN 2 THEN 'IL' WHEN 3 THEN 'TX'
        WHEN 4 THEN 'AZ' WHEN 5 THEN 'PA' WHEN 6 THEN 'TX' WHEN 7 THEN 'CA'
        WHEN 8 THEN 'TX' ELSE 'CA'
    END AS state,
    LPAD((10000 + (random()*89999)::INT)::TEXT, 5, '0') AS zip_code,
    CASE (random()*5)::INT
        WHEN 0 THEN 'employed' WHEN 1 THEN 'employed' WHEN 2 THEN 'employed'
        WHEN 3 THEN 'self_employed' ELSE 'retired'
    END AS employment_status,
    CASE 
        WHEN random() < 0.3 THEN 35000 + (random() * 40000)::INT  -- Lower income
        WHEN random() < 0.7 THEN 75000 + (random() * 75000)::INT  -- Middle income
        ELSE 150000 + (random() * 350000)::INT                    -- High income
    END AS annual_income,
    CASE 
        WHEN random() < 0.1 THEN 300 + (random() * 150)::INT     -- Poor credit
        WHEN random() < 0.3 THEN 450 + (random() * 200)::INT     -- Fair credit  
        WHEN random() < 0.8 THEN 650 + (random() * 150)::INT     -- Good credit
        ELSE 800 + (random() * 50)::INT                          -- Excellent credit
    END AS credit_score,
    CASE 
        WHEN random() < 0.7 THEN 'retail'
        WHEN random() < 0.9 THEN 'premium'
        ELSE 'private_banking'
    END AS customer_segment,
    CASE 
        WHEN random() < 0.7 THEN 'low'
        WHEN random() < 0.9 THEN 'medium'
        ELSE 'high'
    END AS risk_category,
    CASE 
        WHEN random() < 0.95 THEN 'approved'
        ELSE 'under_review'
    END AS kyc_status,
    1 + (random() * 24)::INT AS branch_id
FROM generate_series(1, 1200) AS s(n);

-- Create accounts for customers (1-3 accounts per customer)
WITH customer_accounts AS (
    SELECT 
        customer_id,
        generate_series(1, CASE WHEN random() < 0.5 THEN 1 WHEN random() < 0.8 THEN 2 ELSE 3 END) as account_num
    FROM customers
)
INSERT INTO accounts (customer_id, account_number, account_type, balance, interest_rate, minimum_balance, account_status, overdraft_limit, branch_id, opened_date)
SELECT 
    ca.customer_id,
    'ACC' || LPAD((10000000 + row_number() OVER())::TEXT, 8, '0') AS account_number,
    CASE 
        WHEN ca.account_num = 1 THEN 'checking'
        WHEN ca.account_num = 2 AND random() < 0.7 THEN 'savings'
        WHEN ca.account_num = 2 THEN 'money_market'
        ELSE CASE (random()*3)::INT WHEN 0 THEN 'savings' WHEN 1 THEN 'money_market' ELSE 'certificate_deposit' END
    END AS account_type,
    CASE 
        WHEN ca.account_num = 1 THEN 500 + (random() * 15000)::DECIMAL(10,2)      -- Checking: $500-$15,500
        WHEN ca.account_num = 2 THEN 2000 + (random() * 48000)::DECIMAL(10,2)     -- Savings: $2K-$50K
        ELSE 10000 + (random() * 240000)::DECIMAL(10,2)                           -- Others: $10K-$250K
    END AS balance,
    CASE 
        WHEN ca.account_num = 1 THEN 0.0025    -- Checking: 0.25%
        WHEN ca.account_num = 2 THEN 0.035     -- Savings: 3.5%
        ELSE 0.045                             -- Others: 4.5%
    END AS interest_rate,
    CASE 
        WHEN ca.account_num = 1 THEN 100       -- Checking minimum
        WHEN ca.account_num = 2 THEN 500       -- Savings minimum
        ELSE 5000                              -- Others minimum
    END AS minimum_balance,
    CASE WHEN random() < 0.95 THEN 'active' ELSE 'inactive' END AS account_status,
    CASE WHEN ca.account_num = 1 THEN (random() * 2000)::DECIMAL(8,2) ELSE 0 END AS overdraft_limit,
    c.branch_id,
    DATE '2020-01-01' + (random() * (CURRENT_DATE - DATE '2020-01-01'))::INT AS opened_date
FROM customer_accounts ca
JOIN customers c ON ca.customer_id = c.customer_id;

-- Generate realistic transactions for the last 12 months
INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, transaction_date, merchant_name, merchant_category, location, channel, reference_number, status)
WITH transaction_data AS (
    SELECT 
        a.account_id,
        a.balance as current_balance,
        generate_series(1, CASE WHEN a.account_type = 'checking' THEN 50 + (random() * 150)::INT ELSE 10 + (random() * 30)::INT END) as trans_num
    FROM accounts a
    WHERE a.account_status = 'active'
),
merchants AS (
    SELECT * FROM (VALUES
        ('Amazon', 'Online Retail'), ('Target', 'Retail'), ('Walmart', 'Retail'), ('Starbucks', 'Coffee Shop'),
        ('McDonald''s', 'Fast Food'), ('Shell Gas', 'Gas Station'), ('Uber', 'Transportation'), ('Netflix', 'Entertainment'),
        ('Whole Foods', 'Grocery'), ('CVS Pharmacy', 'Pharmacy'), ('Home Depot', 'Home Improvement'), ('Best Buy', 'Electronics'),
        ('Chipotle', 'Restaurant'), ('Spotify', 'Entertainment'), ('AT&T', 'Utilities'), ('Verizon', 'Utilities'),
        ('Apple Store', 'Electronics'), ('Nike', 'Retail'), ('Costco', 'Retail'), ('Kroger', 'Grocery')
    ) AS t(name, category)
)
SELECT 
    td.account_id,
    CASE 
        WHEN random() < 0.4 THEN 'deposit'
        WHEN random() < 0.7 THEN 'withdrawal'
        WHEN random() < 0.85 THEN 'online'
        ELSE 'atm'
    END AS transaction_type,
    CASE 
        WHEN random() < 0.4 THEN (20 + random() * 2000)::DECIMAL(10,2)  -- Deposits
        ELSE -(5 + random() * 500)::DECIMAL(10,2)                       -- Withdrawals/Purchases
    END AS amount,
    td.current_balance + 
        CASE 
            WHEN random() < 0.4 THEN (20 + random() * 2000)::DECIMAL(10,2)
            ELSE -(5 + random() * 500)::DECIMAL(10,2)
        END AS balance_after,
    CASE 
        WHEN random() < 0.4 THEN 'Direct Deposit - Salary'
        WHEN random() < 0.6 THEN 'Purchase at ' || m.name
        WHEN random() < 0.8 THEN 'ATM Withdrawal'
        ELSE 'Online Transfer'
    END AS description,
    CURRENT_DATE - (random() * 365)::INT + (random() * INTERVAL '24 hours') AS transaction_date,
    CASE WHEN random() < 0.6 THEN m.name ELSE NULL END AS merchant_name,
    CASE WHEN random() < 0.6 THEN m.category ELSE NULL END AS merchant_category,
    CASE (random()*5)::INT
        WHEN 0 THEN 'New York, NY' WHEN 1 THEN 'Los Angeles, CA' WHEN 2 THEN 'Chicago, IL'
        WHEN 3 THEN 'Houston, TX' ELSE 'Online'
    END AS location,
    CASE (random()*4)::INT
        WHEN 0 THEN 'online' WHEN 1 THEN 'mobile' WHEN 2 THEN 'atm' ELSE 'branch'
    END AS channel,
    'TXN' || LPAD((100000000 + (random()*899999999)::BIGINT)::TEXT, 9, '0') AS reference_number,
    CASE WHEN random() < 0.98 THEN 'completed' ELSE 'pending' END AS status
FROM transaction_data td
CROSS JOIN merchants m
ORDER BY random()
LIMIT 50000;

-- Create credit cards for 60% of customers
INSERT INTO credit_cards (customer_id, card_number, card_type, card_category, credit_limit, current_balance, available_credit, apr, annual_fee, card_status, issue_date, expiry_date)
SELECT 
    c.customer_id,
    '4' || LPAD((100000000000000 + (random()*899999999999999)::BIGINT)::TEXT, 15, '0') AS card_number,
    CASE (random()*4)::INT WHEN 0 THEN 'visa' WHEN 1 THEN 'mastercard' WHEN 2 THEN 'amex' ELSE 'discover' END AS card_type,
    CASE 
        WHEN c.credit_score < 600 THEN 'basic'
        WHEN c.credit_score < 720 THEN CASE (random()*2)::INT WHEN 0 THEN 'basic' ELSE 'rewards' END
        WHEN c.credit_score < 780 THEN CASE (random()*3)::INT WHEN 0 THEN 'gold' WHEN 1 THEN 'rewards' ELSE 'cashback' END
        ELSE CASE (random()*2)::INT WHEN 0 THEN 'platinum' ELSE 'gold' END
    END AS card_category,
    CASE 
        WHEN c.credit_score < 600 THEN 1000 + (random() * 2000)::INT
        WHEN c.credit_score < 720 THEN 3000 + (random() * 7000)::INT
        WHEN c.credit_score < 780 THEN 10000 + (random() * 15000)::INT
        ELSE 25000 + (random() * 50000)::INT
    END AS credit_limit,
    0 AS current_balance,
    0 AS available_credit,
    CASE 
        WHEN c.credit_score < 600 THEN 24.99 + (random() * 5)
        WHEN c.credit_score < 720 THEN 19.99 + (random() * 5)
        WHEN c.credit_score < 780 THEN 15.99 + (random() * 4)
        ELSE 12.99 + (random() * 3)
    END AS apr,
    CASE (random()*4)::INT WHEN 0 THEN 0 WHEN 1 THEN 95 WHEN 2 THEN 195 ELSE 495 END AS annual_fee,
    CASE WHEN random() < 0.95 THEN 'active' ELSE 'inactive' END AS card_status,
    DATE '2020-01-01' + (random() * (CURRENT_DATE - DATE '2020-01-01'))::INT AS issue_date,
    CURRENT_DATE + INTERVAL '3 years' AS expiry_date
FROM customers c
WHERE random() < 0.6;  -- 60% of customers get credit cards

-- Update credit card balances and available credit
UPDATE credit_cards SET 
    current_balance = LEAST(credit_limit * 0.8, (random() * credit_limit * 0.5)::DECIMAL(10,2)),
    available_credit = credit_limit - LEAST(credit_limit * 0.8, (random() * credit_limit * 0.5)::DECIMAL(10,2));

-- Generate loans for 30% of customers
INSERT INTO loans (customer_id, loan_number, loan_type, loan_amount, outstanding_balance, interest_rate, term_months, monthly_payment, loan_status, origination_date, maturity_date, next_payment_date, payments_made, collateral_value, ltv_ratio)
SELECT 
    c.customer_id,
    'LOAN' || LPAD((10000000 + row_number() OVER())::TEXT, 7, '0') AS loan_number,
    CASE (random()*5)::INT 
        WHEN 0 THEN 'mortgage' WHEN 1 THEN 'auto' WHEN 2 THEN 'personal' 
        WHEN 3 THEN 'business' ELSE 'student' 
    END AS loan_type,
    CASE 
        WHEN random() < 0.3 THEN 15000 + (random() * 35000)::INT      -- Personal/Auto: $15K-$50K
        WHEN random() < 0.6 THEN 250000 + (random() * 500000)::INT    -- Mortgage: $250K-$750K
        ELSE 50000 + (random() * 200000)::INT                         -- Business: $50K-$250K
    END AS loan_amount,
    0 AS outstanding_balance,  -- Will calculate below
    CASE 
        WHEN random() < 0.3 THEN 6.5 + (random() * 5)     -- 6.5%-11.5%
        WHEN random() < 0.6 THEN 3.5 + (random() * 2)     -- 3.5%-5.5% (mortgage)
        ELSE 8.5 + (random() * 6)                          -- 8.5%-14.5% (business/personal)
    END AS interest_rate,
    CASE 
        WHEN random() < 0.3 THEN 36 + (random() * 48)::INT     -- 3-7 years
        WHEN random() < 0.6 THEN 240 + (random() * 120)::INT   -- 20-30 years (mortgage)
        ELSE 12 + (random() * 48)::INT                          -- 1-5 years
    END AS term_months,
    0 AS monthly_payment,  -- Will calculate below
    CASE WHEN random() < 0.9 THEN 'active' ELSE 'delinquent' END AS loan_status,
    DATE '2020-01-01' + (random() * (CURRENT_DATE - DATE '2020-01-01'))::INT AS origination_date,
    CURRENT_DATE + INTERVAL '10 years' AS maturity_date,
    DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' AS next_payment_date,
    (random() * 36)::INT AS payments_made,
    CASE WHEN random() < 0.6 THEN (50000 + random() * 500000)::DECIMAL(12,2) ELSE NULL END AS collateral_value,
    CASE WHEN random() < 0.6 THEN 75 + (random() * 20) ELSE NULL END AS ltv_ratio
FROM customers c
WHERE random() < 0.3;  -- 30% of customers get loans

-- Update loan outstanding balances and monthly payments
UPDATE loans SET 
    outstanding_balance = loan_amount * (0.3 + random() * 0.7),
    monthly_payment = CASE 
        WHEN loan_type = 'mortgage' THEN loan_amount * 0.005
        WHEN loan_type = 'auto' THEN loan_amount * 0.025
        ELSE loan_amount * 0.035
    END;

-- Create some loan payments
INSERT INTO loan_payments (loan_id, payment_date, payment_amount, principal_amount, interest_amount, payment_method, payment_status)
SELECT 
    l.loan_id,
    CURRENT_DATE - (random() * 365)::INT AS payment_date,
    l.monthly_payment,
    l.monthly_payment * 0.7 AS principal_amount,
    l.monthly_payment * 0.3 AS interest_amount,
    CASE (random()*4)::INT WHEN 0 THEN 'auto_debit' WHEN 1 THEN 'online' WHEN 2 THEN 'branch' ELSE 'mobile' END AS payment_method,
    CASE WHEN random() < 0.98 THEN 'completed' ELSE 'pending' END AS payment_status
FROM loans l
CROSS JOIN generate_series(1, 12) -- Up to 12 payments per loan
WHERE random() < 0.8;  -- 80% of payments are recorded