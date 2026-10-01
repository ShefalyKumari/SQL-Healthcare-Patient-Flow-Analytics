WITH current_active_admissions AS (
    SELECT 
        dept_id,
        COUNT(DISTINCT bed_id) AS occupied_beds,
        AVG(severity_score) AS avg_acuity_score
    FROM encounters
    WHERE discharge_timestamp IS NULL
    GROUP BY dept_id
)

SELECT 
    CASE 
        WHEN d.dept_name LIKE '%Emergency%' THEN 'Emergency'
        WHEN d.dept_name LIKE '%Intensive%' THEN 'ICU'
        WHEN d.dept_name LIKE '%Cardiology%' THEN 'Cardiology'
        WHEN d.dept_name LIKE '%General%' THEN 'Gen Medicine'
        WHEN d.dept_name LIKE '%Surgical%' THEN 'Surgery'
        ELSE d.dept_name 
    END AS "Ward",
    d.total_staffed_beds AS "Beds",
    COALESCE(ca.occupied_beds, 0) AS "Occ",
    (d.total_staffed_beds - COALESCE(ca.occupied_beds, 0)) AS "Avail",
    ROUND(100.0 * COALESCE(ca.occupied_beds, 0) / d.total_staffed_beds, 1) || '%' AS "Occ %",
    CASE 
        WHEN (100.0 * COALESCE(ca.occupied_beds, 0) / d.total_staffed_beds) >= 85.0 THEN 'CRITICAL'
        WHEN (100.0 * COALESCE(ca.occupied_beds, 0) / d.total_staffed_beds) >= 65.0 THEN 'ELEVATED'
        ELSE 'STABLE'
    END AS "Status"
FROM departments d
LEFT JOIN current_active_admissions ca ON d.dept_id = ca.dept_id
ORDER BY (100.0 * COALESCE(ca.occupied_beds, 0) / d.total_staffed_beds) DESC;