-- Add loan data for existing customers
BEGIN;

-- Generate loans for 40% of customers (about 100 loans)
INSERT INTO loans (customer_id, loan_number, loan_type, loan_amount, outstanding_balance, interest_rate, term_months, monthly_payment, loan_status, origination_date, maturity_date, next_payment_date, collateral_value, ltv_ratio)
SELECT 
  c.customer_id,
  'LN' || lpad((c.customer_id - 262)::text, 8, '0') as loan_number,
  CASE (random() * 5)::int
    WHEN 0 THEN 'personal' 
    WHEN 1 THEN 'mortgage' 
    WHEN 2 THEN 'auto' 
    WHEN 3 THEN 'business' 
    WHEN 4 THEN 'student' 
    ELSE 'line_of_credit'
  END as loan_type,
  CASE 
    WHEN random() < 0.2 THEN (5000 + (random() * 45000)::int)::decimal  -- Personal/Student
    WHEN random() < 0.4 THEN (15000 + (random() * 85000)::int)::decimal -- Auto/Business
    WHEN random() < 0.6 THEN (150000 + (random() * 350000)::int)::decimal -- Mortgage
    ELSE (10000 + (random() * 90000)::int)::decimal  -- Line of credit
  END as loan_amount,
  0.00 as outstanding_balance, -- Will be calculated
  (0.025 + (random() * 0.08))::decimal(5,4) as interest_rate,
  CASE (random() * 5)::int
    WHEN 0 THEN 24 
    WHEN 1 THEN 36 
    WHEN 2 THEN 60 
    WHEN 3 THEN 120 
    WHEN 4 THEN 360 
    ELSE 240
  END as term_months,
  0.00 as monthly_payment, -- Will be calculated
  CASE (random() * 5)::int
    WHEN 0 THEN 'active' 
    WHEN 1 THEN 'active' 
    WHEN 2 THEN 'active' 
    WHEN 3 THEN 'paid_off' 
    ELSE 'delinquent'
  END as loan_status,
  (CURRENT_DATE - interval '3 years' + (random() * interval '3 years'))::date as origination_date,
  (CURRENT_DATE + interval '2 years' + (random() * interval '8 years'))::date as maturity_date,
  (CURRENT_DATE + interval '1 month')::date as next_payment_date,
  CASE 
    WHEN random() < 0.3 THEN (50000 + (random() * 200000)::int)::decimal
    ELSE NULL
  END as collateral_value,
  CASE 
    WHEN random() < 0.3 THEN (60 + (random() * 30)::int)::decimal(5,2)
    ELSE NULL
  END as ltv_ratio
FROM customers c
WHERE random() < 0.4  -- 40% of customers get loans
ORDER BY c.customer_id
LIMIT 100;

-- Update outstanding balance and monthly payment for loans
UPDATE loans 
SET outstanding_balance = CASE 
    WHEN loan_status = 'active' THEN loan_amount * (0.4 + random() * 0.6)
    WHEN loan_status = 'delinquent' THEN loan_amount * (0.7 + random() * 0.3)
    ELSE 0.00
  END,
  monthly_payment = CASE 
    WHEN loan_status IN ('active', 'delinquent') THEN 
      GREATEST(50, loan_amount * ((interest_rate/100/12) * power(1 + interest_rate/100/12, term_months)) / (power(1 + interest_rate/100/12, term_months) - 1))
    ELSE 0.00
  END;

-- Generate loan payments for the last 18 months
INSERT INTO loan_payments (loan_id, payment_date, payment_amount, principal_amount, interest_amount, payment_method, payment_status, late_fee)
SELECT 
  l.loan_id,
  (l.origination_date + (payment_month || ' months')::interval)::date as payment_date,
  CASE 
    WHEN l.loan_status = 'active' THEN l.monthly_payment
    WHEN l.loan_status = 'delinquent' AND random() < 0.7 THEN l.monthly_payment * (0.5 + random() * 0.5)
    WHEN l.loan_status = 'paid_off' THEN l.monthly_payment
    ELSE 0.00
  END as payment_amount,
  CASE 
    WHEN l.loan_status = 'active' THEN l.monthly_payment * (0.6 + random() * 0.3)
    WHEN l.loan_status = 'delinquent' THEN l.monthly_payment * (0.4 + random() * 0.4)
    WHEN l.loan_status = 'paid_off' THEN l.monthly_payment * (0.7 + random() * 0.2)
    ELSE 0.00
  END as principal_amount,
  CASE 
    WHEN l.loan_status = 'active' THEN l.monthly_payment * (0.1 + random() * 0.4)
    WHEN l.loan_status = 'delinquent' THEN l.monthly_payment * (0.2 + random() * 0.4)
    WHEN l.loan_status = 'paid_off' THEN l.monthly_payment * (0.1 + random() * 0.3)
    ELSE 0.00
  END as interest_amount,
  CASE (random() * 5)::int
    WHEN 0 THEN 'auto_debit' 
    WHEN 1 THEN 'online' 
    WHEN 2 THEN 'branch' 
    WHEN 3 THEN 'phone' 
    ELSE 'mobile'
  END as payment_method,
  CASE 
    WHEN l.loan_status = 'active' AND random() < 0.95 THEN 'completed'
    WHEN l.loan_status = 'delinquent' AND random() < 0.6 THEN 'completed'
    WHEN l.loan_status = 'paid_off' THEN 'completed'
    WHEN random() < 0.8 THEN 'completed'
    WHEN random() < 0.95 THEN 'pending'
    ELSE 'failed'
  END as payment_status,
  CASE 
    WHEN l.loan_status = 'delinquent' AND random() < 0.4 THEN (25 + random() * 75)::decimal(8,2)
    WHEN random() < 0.05 THEN (15 + random() * 35)::decimal(8,2)
    ELSE 0.00
  END as late_fee
FROM loans l
CROSS JOIN generate_series(1, 18) AS payment_month
WHERE (l.origination_date + (payment_month || ' months')::interval)::date <= CURRENT_DATE
  AND (l.origination_date + (payment_month || ' months')::interval)::date >= l.origination_date;

-- Update payments_made count for loans
UPDATE loans l
SET payments_made = (
  SELECT COUNT(*) 
  FROM loan_payments lp 
  WHERE lp.loan_id = l.loan_id AND lp.payment_status = 'completed'
),
last_payment_date = (
  SELECT MAX(payment_date) 
  FROM loan_payments lp 
  WHERE lp.loan_id = l.loan_id AND lp.payment_status = 'completed'
);

COMMIT;

-- Display updated summary
SELECT 'Loan Data Generation Complete!' as status;
SELECT 
  'Loans' as table_name, 
  COUNT(*) as record_count,
  COUNT(*) FILTER (WHERE loan_status = 'active') as active_loans,
  COUNT(*) FILTER (WHERE loan_status = 'delinquent') as delinquent_loans,
  COUNT(*) FILTER (WHERE loan_status = 'paid_off') as paid_off_loans
FROM loans
UNION ALL
SELECT 
  'Loan Payments', 
  COUNT(*),
  COUNT(*) FILTER (WHERE payment_status = 'completed'),
  COUNT(*) FILTER (WHERE payment_status = 'pending'),
  COUNT(*) FILTER (WHERE payment_status = 'failed')
FROM loan_payments;
