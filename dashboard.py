import duckdb
from tabulate import tabulate

DB_PATH = "healthcare_analytics.db"

def render_dashboard():
    conn = duckdb.connect(DB_PATH)

    # 1. Summary KPIs
    kpi_sql = """
    SELECT 
        (SELECT COUNT(*) FROM patients),
        (SELECT COUNT(*) FROM encounters WHERE discharge_timestamp IS NULL),
        (SELECT SUM(total_staffed_beds) FROM departments),
        ROUND(100.0 * (SELECT COUNT(*) FROM encounters WHERE discharge_timestamp IS NULL) / 
              (SELECT SUM(total_staffed_beds) FROM departments), 1)
    """
    total_patients, active_inpatients, capacity, total_occ = conn.execute(kpi_sql).fetchone()

    # 2. Query Tables
    with open("queries/01_bed_occupancy_saturation.sql", "r") as f:
        occupancy_df = conn.execute(f.read()).df()

    with open("queries/02_30day_readmission_risk.sql", "r") as f:
        readmit_df = conn.execute(f.read()).df()

    with open("queries/03_length_of_stay_analysis.sql", "r") as f:
        los_df = conn.execute(f.read()).df()

    conn.close()

    DIVIDER = "=" * 65

    print("\n" + DIVIDER)
    print("      HOSPITAL OPERATIONS & PATIENT FLOW DASHBOARD")
    print(DIVIDER)

    print("\n[ 1. NETWORK CAPACITY OVERVIEW ]")
    kpis = [
        ["Total Patients", f"{total_patients:,}", "Total Beds", f"{capacity}"],
        ["Current Inpatients", f"{active_inpatients}", "Network Occupancy", f"{total_occ}%"]
    ]
    print(tabulate(kpis, headers=["Metric", "Value", "Capacity Metric", "Value"], tablefmt="rounded_grid"))

    print("\n[ 2. WARD BED OCCUPANCY & STATUS ]")
    print(tabulate(occupancy_df, headers="keys", tablefmt="rounded_grid", showindex=False))

    print("\n[ 3. 30-DAY UNPLANNED READMISSION RATES ]")
    print(tabulate(readmit_df, headers="keys", tablefmt="rounded_grid", showindex=False))

    print("\n[ 4. LENGTH OF STAY (DAYS) BENCHMARKS ]")
    print(tabulate(los_df, headers="keys", tablefmt="rounded_grid", showindex=False))
    print(DIVIDER + "\n")

if __name__ == "__main__":
    render_dashboard()