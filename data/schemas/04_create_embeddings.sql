-- Create schema embeddings from DDL statements
-- This script extracts DDL statements for embedding generation

-- Create a view to extract table definitions for embedding
CREATE OR REPLACE VIEW schema_definitions AS
SELECT
    t.table_name,
    CONCAT(
        'CREATE TABLE ', t.table_name, ' (',
        STRING_AGG(
            CONCAT(
                c.column_name, ' ',
                CASE
                    WHEN c.data_type = 'character varying' THEN CONCAT('VARCHAR(', c.character_maximum_length, ')')
                    WHEN c.data_type = 'numeric' THEN CONCAT('DECIMAL(', c.numeric_precision, ',', c.numeric_scale, ')')
                    WHEN c.data_type = 'integer' THEN 'INTEGER'
                    WHEN c.data_type = 'bigint' THEN 'BIGINT'
                    WHEN c.data_type = 'timestamp without time zone' THEN 'TIMESTAMP'
                    WHEN c.data_type = 'date' THEN 'DATE'
                    WHEN c.data_type = 'boolean' THEN 'BOOLEAN'
                    WHEN c.data_type = 'text' THEN 'TEXT'
                    ELSE UPPER(c.data_type)
                END,
                CASE WHEN c.is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END
            ),
            ', ' ORDER BY c.ordinal_position
        ),
        ');'
    ) as ddl_statement,
    CASE t.table_name
        WHEN 'branches' THEN 'Bank branch locations and contact information'
        WHEN 'customers' THEN 'Customer demographics, employment, and risk information'
        WHEN 'accounts' THEN 'Bank accounts including balance and account type information'
        WHEN 'transactions' THEN 'Account transaction history with amounts and descriptions'
        WHEN 'credit_cards' THEN 'Credit card information including limits and balances'
        WHEN 'credit_card_transactions' THEN 'Credit card transaction history'
        WHEN 'loans' THEN 'Loan information including amounts, terms, and status'
        WHEN 'loan_payments' THEN 'Loan payment history and details'
        ELSE 'Banking related data'
    END as description
FROM
    information_schema.tables t
    JOIN information_schema.columns c ON t.table_name = c.table_name
WHERE
    t.table_schema = 'public'
    AND t.table_type = 'BASE TABLE'
    AND t.table_name IN ('branches', 'customers', 'accounts', 'transactions', 'credit_cards', 'credit_card_transactions', 'loans', 'loan_payments')
GROUP BY t.table_name
ORDER BY t.table_name;