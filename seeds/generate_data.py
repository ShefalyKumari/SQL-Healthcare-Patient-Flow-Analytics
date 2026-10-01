import random
from datetime import date, datetime, timedelta
import duckdb

DB_PATH = "healthcare_analytics.db"

def seed_database():
    conn = duckdb.connect(DB_PATH)
    
    with open("schema/01_init_schema.sql", "r") as f:
        schema_sql = f.read()
    conn.execute(schema_sql)
    print("Healthcare clinical schema initialized.")

    random.seed(42)
    as_of_time = datetime(2026, 4, 1, 12, 0, 0)
    base_history_start = as_of_time - timedelta(days=120)

    # 1. Departments
    depts = [
        ("DEPT-EMERG", "Emergency Department", 20, 1),
        ("DEPT-ICU", "Intensive Care Unit (ICU)", 12, 2),
        ("DEPT-CARD", "Cardiology Specialty", 18, 3),
        ("DEPT-GEN", "General Internal Medicine", 30, 4),
        ("DEPT-SURG", "Post-Surgical Care", 20, 5),
    ]
    conn.executemany("INSERT INTO departments VALUES (?, ?, ?, ?)", depts)

    # 2. Beds
    beds = []
    bed_counter = 1
    for dept_id, dept_name, count, floor in depts:
        b_type = "Ventilator" if "ICU" in dept_name else ("Telemetry" if "Card" in dept_name else "Standard")
        for num in range(1, count + 1):
            bed_id = f"BED-{bed_counter:04d}"
            bed_counter += 1
            code = f"{dept_id.split('-')[1]}-{num:02d}"
            beds.append((bed_id, dept_id, code, b_type))
    conn.executemany("INSERT INTO beds VALUES (?, ?, ?, ?)", beds)

    # 3. Patients (120 clinical patient records)
    genders = ["Female", "Male"]
    blood_groups = ["O+", "A+", "B+", "AB+", "O-", "A-"]
    patients = []
    for i in range(1, 121):
        pid = f"PAT-{i:04d}"
        mrn = f"MRN-2026-{i:05d}"
        dob = date(1945, 1, 1) + timedelta(days=random.randint(0, 24000))
        chronic = random.random() < 0.40 # 40% with chronic co-morbidities
        patients.append((pid, mrn, f"Patient_Record_{i}", dob, random.choice(genders), random.choice(blood_groups), chronic))
    conn.executemany("INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?)", patients)

    # 4. Clinical Encounters & Readmission Scenarios
    encounters = []
    vitals = []
    enc_counter = 1
    vital_counter = 1

    icd_codes = ["I50.9 (Heart Failure)", "J44.1 (COPD Exacerbation)", "E11.9 (Type 2 Diabetes)", "A41.9 (Sepsis)", "K56.6 (Intestinal Obstruction)"]
    dispositions = ["Home", "Skilled_Nursing", "Transferred"]

    for pat in patients:
        pat_id = pat[0]
        is_chronic = pat[6]
        
        # Primary Encounter
        admit_dt = base_history_start + timedelta(days=random.randint(5, 70), hours=random.randint(0, 23))
        dept = random.choice(depts)
        available_beds = [b[0] for b in beds if b[1] == dept[0]]
        bed_assigned = random.choice(available_beds) if available_beds else None
        
        # Length of stay: 1 to 9 days
        los_hours = random.randint(24, 180) if "ICU" not in dept[1] else random.randint(48, 260)
        discharge_dt = admit_dt + timedelta(hours=los_hours)
        enc_id = f"ENC-{enc_counter:06d}"
        enc_counter += 1
        
        diag = random.choice(icd_codes)
        severity = random.randint(3, 5) if is_chronic else random.randint(1, 3)
        dispo = random.choice(dispositions)
        encounters.append((enc_id, pat_id, dept[0], bed_assigned, "Inpatient", admit_dt, discharge_dt, dispo, diag, severity))

        # Add Vitals during stay
        for step in range(3):
            v_time = admit_dt + timedelta(hours=step * 12 + 2)
            vitals.append((f"VIT-{vital_counter:06d}", enc_id, v_time, random.randint(62, 115), random.randint(95, 155), round(random.uniform(92.0, 99.5), 1)))
            vital_counter += 1

        # Readmission Typology (High risk for chronic patients within 30-day CMS window)
        if is_chronic and random.random() < 0.45:
            readmit_dt = discharge_dt + timedelta(days=random.randint(3, 26), hours=random.randint(1, 8))
            if readmit_dt < as_of_time:
                readmit_dept = "DEPT-ICU" if random.random() < 0.50 else dept[0]
                readmit_bed = random.choice([b[0] for b in beds if b[1] == readmit_dept])
                readmit_los = random.randint(36, 160)
                readmit_disch = readmit_dt + timedelta(hours=readmit_los)
                readmit_enc_id = f"ENC-{enc_counter:06d}"
                enc_counter += 1
                encounters.append((readmit_enc_id, pat_id, readmit_dept, readmit_bed, "Inpatient", readmit_dt, readmit_disch, "Home", diag, 4))
        
        # Currently Active Inpatients (Admitted within last 4 days, no discharge yet)
        if random.random() < 0.20:
            curr_admit = as_of_time - timedelta(hours=random.randint(6, 72))
            curr_dept = random.choice(depts)
            curr_bed = random.choice([b[0] for b in beds if b[1] == curr_dept[0]])
            curr_enc_id = f"ENC-{enc_counter:06d}"
            enc_counter += 1
            encounters.append((curr_enc_id, pat_id, curr_dept[0], curr_bed, "Inpatient", curr_admit, None, None, random.choice(icd_codes), random.randint(2, 5)))

    conn.executemany("INSERT INTO encounters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", encounters)
    conn.executemany("INSERT INTO vitals_log VALUES (?, ?, ?, ?, ?, ?)", vitals)

    print("Healthcare dataset seeded successfully:")
    print(f" - Departments: {len(depts)}")
    print(f" - Beds:        {len(beds)}")
    print(f" - Patients:    {len(patients)}")
    print(f" - Encounters:  {len(encounters)}")
    print(f" - Vitals Logs: {len(vitals)}")
    conn.close()

if __name__ == "__main__":
    seed_database()