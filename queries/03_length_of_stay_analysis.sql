WITH completed_stays AS (
    SELECT 
        CASE 
            WHEN d.dept_name LIKE '%Emergency%' THEN 'Emergency'
            WHEN d.dept_name LIKE '%Intensive%' THEN 'ICU'
            WHEN d.dept_name LIKE '%Cardiology%' THEN 'Cardiology'
            WHEN d.dept_name LIKE '%General%' THEN 'Gen Medicine'
            WHEN d.dept_name LIKE '%Surgical%' THEN 'Surgery'
            ELSE d.dept_name 
        END AS ward,
        ROUND(EXTRACT(EPOCH FROM (e.discharge_timestamp - e.admit_timestamp)) / 86400.0, 1) AS los_days
    FROM encounters e
    JOIN departments d ON e.dept_id = d.dept_id
    WHERE e.discharge_timestamp IS NOT NULL
)

SELECT 
    ward AS "Ward",
    COUNT(*) AS "Discharges",
    ROUND(AVG(los_days), 1) AS "Mean LOS",
    ROUND(MIN(los_days), 1) AS "Min",
    ROUND(MAX(los_days), 1) AS "Max",
    ROUND(AVG(los_days) + (2 * STDDEV(los_days)), 1) AS "Outlier"
FROM completed_stays
GROUP BY ward
ORDER BY AVG(los_days) DESC;