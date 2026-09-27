SELECT
    customer_id,
    status
FROM analytics.dim_customer_status
WHERE status = 'VIP'
