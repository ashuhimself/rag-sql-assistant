-- Sample Banking Data for RAG SQL Assistant Demo
-- This script populates the banking database with realistic test data

-- Insert Branches
INSERT INTO branches (branch_name, branch_code, address, city, state, zip_code, phone) VALUES
('Downtown Main Branch', 'DTM001', '123 Main Street', 'New York', 'NY', '10001', '(555) 123-4567'),
('Uptown Financial Center', 'UFC002', '456 Park Avenue', 'New York', 'NY', '10022', '(555) 234-5678'),
('Brooklyn Heights Branch', 'BHB003', '789 Heights Blvd', 'Brooklyn', 'NY', '11201', '(555) 345-6789'),
('Queens Plaza Branch', 'QPB004', '321 Plaza Drive', 'Queens', 'NY', '11101', '(555) 456-7890'),
('Staten Island Branch', 'SIB005', '654 Island Way', 'Staten Island', 'NY', '10301', '(555) 567-8901');

-- Insert Customers
INSERT INTO customers (first_name, last_name, email, phone, date_of_birth, ssn, address, city, state, zip_code, employment_status, annual_income, credit_score, customer_segment, risk_category, kyc_status, branch_id) VALUES
-- High-value customers
('John', 'Anderson', 'john.anderson@email.com', '(555) 111-1111', '1985-03-15', '123-45-6789', '100 Luxury Lane', 'New York', 'NY', '10001', 'employed', 150000.00, 780, 'premium', 'low', 'approved', 1),
('Sarah', 'Williams', 'sarah.williams@email.com', '(555) 222-2222', '1978-07-22', '234-56-7890', '200 Executive Drive', 'New York', 'NY', '10022', 'employed', 200000.00, 810, 'premium', 'low', 'approved', 2),
('Michael', 'Davis', 'michael.davis@email.com', '(555) 333-3333', '1982-11-08', '345-67-8901', '300 Success Street', 'Brooklyn', 'NY', '11201', 'self_employed', 180000.00, 750, 'premium', 'medium', 'approved', 3),

-- Regular customers
('Emily', 'Johnson', 'emily.johnson@email.com', '(555) 444-4444', '1990-05-12', '456-78-9012', '400 Regular Road', 'Queens', 'NY', '11101', 'employed', 75000.00, 720, 'retail', 'low', 'approved', 4),
('David', 'Brown', 'david.brown@email.com', '(555) 555-5555', '1987-09-30', '567-89-0123', '500 Normal Ave', 'Staten Island', 'NY', '10301', 'employed', 65000.00, 690, 'retail', 'medium', 'approved', 5),
('Lisa', 'Wilson', 'lisa.wilson@email.com', '(555) 666-6666', '1993-02-18', '678-90-1234', '600 Standard St', 'New York', 'NY', '10001', 'employed', 55000.00, 710, 'retail', 'low', 'approved', 1),
('James', 'Miller', 'james.miller@email.com', '(555) 777-7777', '1979-12-03', '789-01-2345', '700 Common Circle', 'Brooklyn', 'NY', '11201', 'employed', 85000.00, 730, 'retail', 'low', 'approved', 3),
('Jennifer', 'Garcia', 'jennifer.garcia@email.com', '(555) 888-8888', '1986-08-25', '890-12-3456', '800 Typical Terrace', 'Queens', 'NY', '11101', 'employed', 70000.00, 680, 'retail', 'medium', 'approved', 4),

-- Students and lower income
('Robert', 'Martinez', 'robert.martinez@email.com', '(555) 999-9999', '1995-04-10', '901-23-4567', '900 Student Street', 'New York', 'NY', '10001', 'student', 25000.00, 650, 'retail', 'medium', 'approved', 1),
('Amanda', 'Taylor', 'amanda.taylor@email.com', '(555) 000-0000', '1992-06-15', '012-34-5678', '1000 College Ave', 'Brooklyn', 'NY', '11201', 'student', 20000.00, 630, 'retail', 'medium', 'approved', 3);

-- Insert Accounts
INSERT INTO accounts (customer_id, account_number, account_type, balance, interest_rate, minimum_balance, account_status, overdraft_limit, branch_id, opened_date) VALUES
-- Checking accounts
(1, '1001001001', 'checking', 15000.00, 0.0100, 1000.00, 'active', 2000.00, 1, '2020-01-15'),
(2, '1002001002', 'checking', 25000.00, 0.0100, 1000.00, 'active', 5000.00, 2, '2019-03-22'),
(3, '1003001003', 'checking', 18000.00, 0.0100, 1000.00, 'active', 3000.00, 3, '2021-05-10'),
(4, '1004001004', 'checking', 8500.00, 0.0100, 500.00, 'active', 1000.00, 4, '2022-02-18'),
(5, '1005001005', 'checking', 6200.00, 0.0100, 500.00, 'active', 500.00, 5, '2021-11-30'),
(6, '1006001006', 'checking', 4800.00, 0.0100, 500.00, 'active', 500.00, 1, '2023-01-15'),
(7, '1007001007', 'checking', 9200.00, 0.0100, 500.00, 'active', 1000.00, 3, '2020-08-12'),
(8, '1008001008', 'checking', 7100.00, 0.0100, 500.00, 'active', 750.00, 4, '2022-04-25'),
(9, '1009001009', 'checking', 1200.00, 0.0100, 100.00, 'active', 200.00, 1, '2023-09-10'),
(10, '1010001010', 'checking', 800.00, 0.0100, 100.00, 'active', 100.00, 3, '2024-01-20'),

-- Savings accounts
(1, '2001001001', 'savings', 45000.00, 0.0250, 100.00, 'active', 0.00, 1, '2020-01-15'),
(2, '2002001002', 'savings', 78000.00, 0.0250, 100.00, 'active', 0.00, 2, '2019-03-22'),
(3, '2003001003', 'savings', 52000.00, 0.0250, 100.00, 'active', 0.00, 3, '2021-05-10'),
(4, '2004001004', 'savings', 23000.00, 0.0250, 100.00, 'active', 0.00, 4, '2022-02-18'),
(5, '2005001005', 'savings', 18500.00, 0.0250, 100.00, 'active', 0.00, 5, '2021-11-30'),
(6, '2006001006', 'savings', 15200.00, 0.0250, 100.00, 'active', 0.00, 1, '2023-01-15'),
(7, '2007001007', 'savings', 28000.00, 0.0250, 100.00, 'active', 0.00, 3, '2020-08-12'),
(8, '2008001008', 'savings', 19800.00, 0.0250, 100.00, 'active', 0.00, 4, '2022-04-25'),

-- Business accounts for self-employed customer
(3, '3003001003', 'business_checking', 35000.00, 0.0050, 2500.00, 'active', 10000.00, 3, '2021-06-01');

-- Insert Credit Cards
INSERT INTO credit_cards (customer_id, card_number, card_type, card_category, credit_limit, current_balance, available_credit, apr, annual_fee, card_status, issue_date, expiry_date) VALUES
(1, '4111111111111111', 'visa', 'platinum', 25000.00, 3200.00, 21800.00, 18.99, 95.00, 'active', '2020-02-01', '2025-02-01'),
(2, '4222222222222222', 'visa', 'platinum', 50000.00, 8500.00, 41500.00, 16.99, 150.00, 'active', '2019-04-15', '2024-04-15'),
(3, '4333333333333333', 'mastercard', 'gold', 20000.00, 4200.00, 15800.00, 19.99, 75.00, 'active', '2021-06-10', '2026-06-10'),
(4, '4444444444444444', 'visa', 'rewards', 15000.00, 2800.00, 12200.00, 21.99, 0.00, 'active', '2022-03-20', '2027-03-20'),
(5, '4555555555555555', 'mastercard', 'cashback', 10000.00, 1500.00, 8500.00, 22.99, 0.00, 'active', '2022-01-15', '2027-01-15'),
(6, '4666666666666666', 'visa', 'basic', 5000.00, 800.00, 4200.00, 24.99, 0.00, 'active', '2023-02-28', '2028-02-28'),
(7, '4777777777777777', 'mastercard', 'rewards', 12000.00, 2100.00, 9900.00, 20.99, 50.00, 'active', '2020-09-12', '2025-09-12'),
(8, '4888888888888888', 'visa', 'cashback', 8000.00, 1200.00, 6800.00, 23.99, 0.00, 'active', '2022-05-18', '2027-05-18');

-- Insert Recent Transactions (last 30 days)
INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, transaction_date, merchant_name, merchant_category, location, channel, reference_number, status) VALUES
-- John Anderson's transactions
(1, 'deposit', 5000.00, 15000.00, 'Salary deposit', '2024-09-25 09:30:00', 'Employer Direct Deposit', 'Payroll', 'New York, NY', 'online', 'TXN001', 'completed'),
(1, 'withdrawal', 500.00, 14500.00, 'ATM withdrawal', '2024-09-24 14:15:00', 'Chase ATM', 'ATM', 'New York, NY', 'atm', 'TXN002', 'completed'),
(1, 'transfer_out', 2000.00, 12500.00, 'Transfer to savings', '2024-09-23 10:20:00', 'Internal Transfer', 'Transfer', 'Online', 'online', 'TXN003', 'completed'),

-- Sarah Williams' transactions
(2, 'deposit', 8000.00, 25000.00, 'Salary deposit', '2024-09-25 09:30:00', 'Employer Direct Deposit', 'Payroll', 'New York, NY', 'online', 'TXN004', 'completed'),
(2, 'withdrawal', 200.00, 24800.00, 'Coffee shop', '2024-09-24 08:45:00', 'Starbucks', 'Food & Beverage', 'New York, NY', 'mobile', 'TXN005', 'completed'),
(2, 'withdrawal', 1200.00, 23600.00, 'Grocery shopping', '2024-09-22 17:30:00', 'Whole Foods', 'Grocery', 'New York, NY', 'mobile', 'TXN006', 'completed'),

-- More transactions for other customers
(4, 'deposit', 3000.00, 8500.00, 'Salary deposit', '2024-09-25 09:30:00', 'Employer Direct Deposit', 'Payroll', 'Queens, NY', 'online', 'TXN007', 'completed'),
(4, 'withdrawal', 150.00, 8350.00, 'Gas station', '2024-09-24 18:20:00', 'Shell', 'Gas Station', 'Queens, NY', 'mobile', 'TXN008', 'completed'),
(5, 'deposit', 2500.00, 6200.00, 'Salary deposit', '2024-09-25 09:30:00', 'Employer Direct Deposit', 'Payroll', 'Staten Island, NY', 'online', 'TXN009', 'completed'),
(6, 'withdrawal', 80.00, 4720.00, 'Restaurant', '2024-09-23 19:45:00', 'Olive Garden', 'Restaurant', 'New York, NY', 'mobile', 'TXN010', 'completed'),
(7, 'deposit', 3500.00, 9200.00, 'Salary deposit', '2024-09-25 09:30:00', 'Employer Direct Deposit', 'Payroll', 'Brooklyn, NY', 'online', 'TXN011', 'completed'),
(8, 'withdrawal', 300.00, 6800.00, 'Online shopping', '2024-09-22 14:10:00', 'Amazon', 'Online Retail', 'Online', 'online', 'TXN012', 'completed');

-- Insert Credit Card Transactions
INSERT INTO credit_card_transactions (card_id, transaction_type, amount, merchant_name, merchant_category, transaction_date, location, reference_number, status, rewards_earned) VALUES
(1, 'purchase', 1200.00, 'Best Buy', 'Electronics', '2024-09-24 15:30:00', 'New York, NY', 'CC001', 'completed', 12.00),
(1, 'purchase', 85.00, 'Shell', 'Gas Station', '2024-09-23 09:15:00', 'New York, NY', 'CC002', 'completed', 0.85),
(2, 'purchase', 2500.00, 'Apple Store', 'Electronics', '2024-09-22 11:45:00', 'New York, NY', 'CC003', 'completed', 50.00),
(2, 'purchase', 180.00, 'Le Bernardin', 'Restaurant', '2024-09-21 20:30:00', 'New York, NY', 'CC004', 'completed', 3.60),
(3, 'purchase', 450.00, 'Home Depot', 'Home Improvement', '2024-09-25 13:20:00', 'Brooklyn, NY', 'CC005', 'completed', 4.50),
(4, 'purchase', 320.00, 'Target', 'Retail', '2024-09-24 16:45:00', 'Queens, NY', 'CC006', 'completed', 6.40),
(5, 'purchase', 95.00, 'CVS Pharmacy', 'Pharmacy', '2024-09-23 12:30:00', 'Staten Island, NY', 'CC007', 'completed', 0.95);

-- Insert Loans
INSERT INTO loans (customer_id, loan_number, loan_type, loan_amount, outstanding_balance, interest_rate, term_months, monthly_payment, loan_status, origination_date, maturity_date, next_payment_date, payments_made, last_payment_date, collateral_value, ltv_ratio) VALUES
(1, 'MTG-001-2020', 'mortgage', 750000.00, 680000.00, 0.0325, 360, 3266.00, 'active', '2020-06-01', '2050-06-01', '2024-10-01', 52, '2024-09-01', 950000.00, 78.95),
(2, 'MTG-002-2019', 'mortgage', 1200000.00, 1050000.00, 0.0285, 360, 4984.00, 'active', '2019-08-15', '2049-08-15', '2024-10-15', 63, '2024-09-15', 1500000.00, 80.00),
(3, 'AUTO-003-2022', 'auto', 45000.00, 32000.00, 0.0450, 60, 838.00, 'active', '2022-03-10', '2027-03-10', '2024-10-10', 30, '2024-09-10', 35000.00, 91.43),
(4, 'PER-004-2023', 'personal', 25000.00, 18500.00, 0.0850, 60, 512.00, 'active', '2023-01-20', '2028-01-20', '2024-10-20', 21, '2024-09-20', NULL, NULL),
(7, 'AUTO-007-2021', 'auto', 35000.00, 22000.00, 0.0420, 72, 575.00, 'active', '2021-04-15', '2027-04-15', '2024-10-15', 42, '2024-09-15', 28000.00, 78.57);

-- Insert Loan Payments
INSERT INTO loan_payments (loan_id, payment_date, payment_amount, principal_amount, interest_amount, fee_amount, payment_method, payment_status, late_fee) VALUES
-- Recent payments for active loans
(1, '2024-09-01', 3266.00, 1436.00, 1830.00, 0.00, 'auto_debit', 'completed', 0.00),
(1, '2024-08-01', 3266.00, 1432.00, 1834.00, 0.00, 'auto_debit', 'completed', 0.00),
(2, '2024-09-15', 4984.00, 2484.00, 2500.00, 0.00, 'auto_debit', 'completed', 0.00),
(2, '2024-08-15', 4984.00, 2480.00, 2504.00, 0.00, 'auto_debit', 'completed', 0.00),
(3, '2024-09-10', 838.00, 718.00, 120.00, 0.00, 'online', 'completed', 0.00),
(3, '2024-08-10', 838.00, 715.00, 123.00, 0.00, 'online', 'completed', 0.00),
(4, '2024-09-20', 512.00, 381.00, 131.00, 0.00, 'auto_debit', 'completed', 0.00),
(4, '2024-08-20', 512.00, 378.00, 134.00, 0.00, 'auto_debit', 'completed', 0.00),
(5, '2024-09-15', 575.00, 498.00, 77.00, 0.00, 'online', 'completed', 0.00),
(5, '2024-08-15', 575.00, 495.00, 80.00, 0.00, 'online', 'completed', 0.00);