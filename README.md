# 🎓 HigherEd Data Reconciler

A free, open-source **Excel and CSV discrepancy calculator** for higher-education CRM, SIS, admissions, and data operations teams. Upload two datasets, map IDs and fields, identify mismatches, and export an Excel reconciliation report.

**Live demo:** Add your Streamlit deployment URL here after publishing.

## Features
- Upload `.csv` or `.xlsx` files
- Map different ID column names across sources
- Map different comparison column names
- Detect mismatched field values, missing IDs, duplicate IDs, and blank IDs
- Download a multi-sheet `.xlsx` reconciliation report
- Preserve leading zeros in student IDs by reading columns as text
- Optional case-insensitive comparison

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL displayed by Streamlit, typically http://localhost:8501.

## Try the demo
Upload `sample_data/sample_source_a.xlsx` and `sample_data/sample_source_b.xlsx`. Select **Student ID** in both files, then map corresponding fields and run reconciliation. The sample files are synthetic.

## How reconciliation works
- Rows are matched on exact ID values (with leading/trailing whitespace removed).
- IDs duplicated in either file are flagged and **excluded from comparisons** rather than silently merged.
- Rows with blank IDs are flagged and excluded.
- Missing IDs are listed in separate report sheets.
- Each differing field creates one difference row; mismatch rate counts **unique IDs**, not field differences.
- Text values are compared exactly except outer whitespace; optional case-insensitive mode is available.
- Excel reads the first sheet. No formula evaluation or automatic domain-specific code normalization.

## Data protection
**The public demo is not approved for FERPA-protected or other restricted student data.** Hosted uploads are processed on the hosting server. Use synthetic/non-sensitive datasets in the public app. For institutional data, run locally only if your institution's policies permit it, or deploy to an institutionally approved environment. This app does not provide authentication, audit logging, or an institutional compliance certification.

## Tech stack
Python · pandas · Streamlit · openpyxl

## Development
```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q
```

## License
MIT. See LICENSE.
