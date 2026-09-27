CREATE OR REPLACE TABLE analytics.stg_orders AS
SELECT
    order_id,
    customer_id,
    order_amount
FROM raw.orders
