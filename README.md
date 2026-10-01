# Healthcare Patient Flow, Bed Allocation & Readmission Risk Engine

A production-grade SQL clinical data engineering and operational analytics engine modeling hospital department bed capacity saturation, CMS 30-day unplanned readmission rates, and ward-level Length of Stay (LOS) distributions.

---

## Relational Entity-Relationship Model (ERD)

```text
[patients] 1 ────< [encounters] >──── 1 [departments] 1 ────< [beds]
                         │
                         ├──────── 1 ────< [beds]
                         │
                         └──────── 1 ────< [vitals_log]