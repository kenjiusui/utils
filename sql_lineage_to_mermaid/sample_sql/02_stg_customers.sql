CREATE TABLE analytics.stg_customers AS
SELECT
    customer_id,
    customer_name
FROM raw.customers
