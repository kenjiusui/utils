INSERT INTO analytics.fct_order_summary
WITH orders_with_customer AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_amount,
        c.customer_name
    FROM analytics.stg_orders AS o
    LEFT JOIN analytics.stg_customers AS c
        ON o.customer_id = c.customer_id
)
SELECT
    customer_id,
    customer_name,
    SUM(order_amount) AS total_amount
FROM orders_with_customer
GROUP BY customer_id, customer_name
