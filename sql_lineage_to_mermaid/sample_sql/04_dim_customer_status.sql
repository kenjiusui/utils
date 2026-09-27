MERGE INTO analytics.dim_customer_status AS tgt
USING (
    SELECT
        customer_id,
        total_amount,
        CASE WHEN total_amount > 10000 THEN 'VIP' ELSE 'REGULAR' END AS status
    FROM analytics.fct_order_summary
) AS src
ON tgt.customer_id = src.customer_id
WHEN MATCHED THEN
    UPDATE SET status = src.status
WHEN NOT MATCHED THEN
    INSERT (customer_id, status) VALUES (src.customer_id, src.status)
