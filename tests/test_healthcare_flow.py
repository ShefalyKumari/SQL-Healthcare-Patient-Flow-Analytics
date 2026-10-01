import duckdb
import pytest

DB_PATH = "healthcare_analytics.db"

@pytest.fixture
def db_conn():
    conn = duckdb.connect(DB_PATH)
    yield conn
    conn.close()

def test_database_populated(db_conn):
    pat_count = db_conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    dept_count = db_conn.execute("SELECT COUNT(*) FROM departments").fetchone()[0]
    enc_count = db_conn.execute("SELECT COUNT(*) FROM encounters").fetchone()[0]
    assert pat_count == 120
    assert dept_count == 5
    assert enc_count > 100

def test_bed_occupancy_bounds(db_conn):
    with open("queries/01_bed_occupancy_saturation.sql", "r") as f:
        query = f.read()
    df = db_conn.execute(query).df()
    
    assert len(df) == 5, "Must evaluate all 5 hospital departments"
    assert (df["Occ"] >= 0).all()
    assert (df["Avail"] >= 0).all()

def test_readmission_rate_validity(db_conn):
    with open("queries/02_30day_readmission_risk.sql", "r") as f:
        query = f.read()
    df = db_conn.execute(query).df()
    
    assert len(df) > 0
    total_readmits = df["Readmits"].sum()
    assert total_readmits > 0, "Readmissions query must detect readmitted patients"

def test_length_of_stay_positive(db_conn):
    with open("queries/03_length_of_stay_analysis.sql", "r") as f:
        query = f.read()
    df = db_conn.execute(query).df()
    
    assert len(df) > 0
    assert (df["Mean LOS"] > 0).all()
    assert (df["Max"] >= df["Mean LOS"]).all()