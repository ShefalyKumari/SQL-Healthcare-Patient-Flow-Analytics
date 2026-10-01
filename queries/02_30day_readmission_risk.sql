WITH encounter_timeline AS (
    SELECT 
        encounter_id,
        patient_id,
        primary_diagnosis_code,
        admit_timestamp,
        discharge_timestamp,
        LEAD(admit_timestamp) OVER (
            PARTITION BY patient_id 
            ORDER BY admit_timestamp
        ) AS next_admit_timestamp
    FROM encounters
    WHERE encounter_type = 'Inpatient'
      AND discharge_timestamp IS NOT NULL
),

readmission_flags AS (
    SELECT 
        CASE 
            WHEN primary_diagnosis_code LIKE '%Heart%' THEN 'Heart Failure'
            WHEN primary_diagnosis_code LIKE '%COPD%' THEN 'COPD Exacerb.'
            WHEN primary_diagnosis_code LIKE '%Diabetes%' THEN 'Type 2 Diabetes'
            WHEN primary_diagnosis_code LIKE '%Sepsis%' THEN 'Sepsis'
            WHEN primary_diagnosis_code LIKE '%Obstruction%' THEN 'GI Obstruction'
            ELSE SUBSTR(primary_diagnosis_code, 1, 15)
        END AS diagnosis,
        CASE 
            WHEN next_admit_timestamp IS NOT NULL 
             AND EXTRACT(EPOCH FROM (next_admit_timestamp - discharge_timestamp)) / 86400.0 <= 30.0 
            THEN 1 
            ELSE 0 
        END AS is_30d_readmit
    FROM encounter_timeline
)

SELECT 
    diagnosis AS "Diagnosis",
    COUNT(*) AS "Discharges",
    SUM(is_30d_readmit) AS "Readmits",
    ROUND(100.0 * SUM(is_30d_readmit) / COUNT(*), 1) || '%' AS "Rate"
FROM readmission_flags
GROUP BY diagnosis
ORDER BY SUM(is_30d_readmit) DESC;