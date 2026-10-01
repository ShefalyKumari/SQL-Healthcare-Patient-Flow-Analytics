DROP TABLE IF EXISTS vitals_log;
DROP TABLE IF EXISTS encounters;
DROP TABLE IF EXISTS beds;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS patients;

-- 1. Patients Master Entity
CREATE TABLE patients (
    patient_id VARCHAR(16) PRIMARY KEY,
    mrn VARCHAR(32) NOT NULL UNIQUE, -- Medical Record Number
    full_name VARCHAR(64) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(16) NOT NULL,
    blood_group VARCHAR(8) NOT NULL,
    chronic_condition_flag BOOLEAN NOT NULL DEFAULT FALSE
);

-- 2. Hospital Departments / Wards
CREATE TABLE departments (
    dept_id VARCHAR(16) PRIMARY KEY,
    dept_name VARCHAR(48) NOT NULL, -- ICU, Cardiology, Oncology, Emergency, General Ward
    total_staffed_beds INTEGER NOT NULL CHECK (total_staffed_beds > 0),
    floor_number INTEGER NOT NULL
);

-- 3. Bed Asset Allocation
CREATE TABLE beds (
    bed_id VARCHAR(16) PRIMARY KEY,
    dept_id VARCHAR(16) NOT NULL REFERENCES departments(dept_id),
    bed_code VARCHAR(16) NOT NULL UNIQUE,
    bed_type VARCHAR(24) NOT NULL CHECK (bed_type IN ('Standard', 'Telemetry', 'Negative_Pressure', 'Ventilator'))
);

-- 4. Clinical Encounters (Admissions & Discharges)
CREATE TABLE encounters (
    encounter_id VARCHAR(16) PRIMARY KEY,
    patient_id VARCHAR(16) NOT NULL REFERENCES patients(patient_id),
    dept_id VARCHAR(16) NOT NULL REFERENCES departments(dept_id),
    bed_id VARCHAR(16) REFERENCES beds(bed_id),
    encounter_type VARCHAR(24) NOT NULL CHECK (encounter_type IN ('Inpatient', 'Emergency', 'Observation', 'Ambulatory')),
    admit_timestamp TIMESTAMP NOT NULL,
    discharge_timestamp TIMESTAMP, -- NULL indicates currently admitted
    discharge_disposition VARCHAR(32) CHECK (discharge_disposition IN ('Home', 'Skilled_Nursing', 'Transferred', 'Deceased', 'AMA')),
    primary_diagnosis_code VARCHAR(16) NOT NULL, -- ICD-10 Category
    severity_score INTEGER NOT NULL CHECK (severity_score BETWEEN 1 AND 5)
);

-- 5. In-Stay Clinical Vitals Log (Granular Events)
CREATE TABLE vitals_log (
    vital_id VARCHAR(16) PRIMARY KEY,
    encounter_id VARCHAR(16) NOT NULL REFERENCES encounters(encounter_id),
    recorded_at TIMESTAMP NOT NULL,
    heart_rate INTEGER NOT NULL,
    systolic_bp INTEGER NOT NULL,
    oxygen_saturation NUMERIC(4, 1) NOT NULL
);