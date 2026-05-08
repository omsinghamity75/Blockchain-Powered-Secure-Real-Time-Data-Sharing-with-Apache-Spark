# Blockchain-Powered Secure Real-Time Data Sharing with Apache Spark

This project is a fuller academic-project model for secure data sharing. It combines:

- `Flask` for an API layer
- a `blockchain-inspired audit ledger` for tamper-evident tracking
- `Apache Spark` for analytics-style data processing
- persistent JSON storage for a simple local demo

## Project Structure

```text
.
|-- backend
|   |-- app.py
|   |-- blockchain.py
|   |-- storage.py
|   `-- __init__.py
|-- data
|   `-- sample_events.jsonl
|-- spark
|   `-- streaming_job.py
|-- tests
|   |-- test_blockchain.py
|   `-- test_storage.py
|-- .gitignore
|-- requirements.txt
`-- README.md
```

## Core Features

- Share records through a REST API
- Persist records locally in `data/shared_records.json`
- Maintain a tamper-evident ledger in `data/ledger.json`
- Verify ledger integrity at any time
- Bootstrap the system with sample sensor data
- View simple analytics by owner, source, and alert count
- Run a Spark data-processing demo that works on Windows

## API Endpoints

- `GET /` : service health and endpoint list
- `POST /share` : add a secure shared record
- `POST /bootstrap` : load sample records from `data/sample_events.jsonl`
- `GET /records` : list all stored records
- `GET /analytics` : summary statistics
- `GET /ledger` : full blockchain ledger
- `GET /ledger/verify` : integrity check
- `GET /dashboard` : browser dashboard

## PowerShell Commands To Run

Create the environment:

```powershell
python -m venv .venv
& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt
```

Run the backend:

```powershell
& ".\.venv\Scripts\python.exe" "backend\app.py"
```

Load sample records:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/bootstrap
```

Share one custom record:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/share `
  -ContentType "application/json" `
  -Body '{"source":"sensor-x","owner":"team-omega","payload":{"temperature":33,"humidity":57},"classification":"restricted"}'
```

View analytics:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/analytics
```

Run tests:

```powershell
& ".\.venv\Scripts\pytest.exe"
```

Run the Spark pipeline:

```powershell
& ".\.venv\Scripts\python.exe" "spark\streaming_job.py"
```

## Expected Spark Output

The Spark script prints a table with:

- sensor source
- owner team
- temperature and humidity
- alert status
- processed timestamp


