import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

try:
    from .blockchain import SimpleBlockchain
    from .storage import RecordStore
except ImportError:
    from blockchain import SimpleBlockchain
    from storage import RecordStore


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RECORDS_FILE = DATA_DIR / "shared_records.json"
CHAIN_FILE = DATA_DIR / "ledger.json"
SAMPLE_FILE = DATA_DIR / "sample_events.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_chain() -> List[Dict[str, Any]] | None:
    if not CHAIN_FILE.exists():
        return None
    with CHAIN_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_chain(ledger: SimpleBlockchain) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CHAIN_FILE.open("w", encoding="utf-8") as handle:
        json.dump(ledger.to_list(), handle, indent=2)


def _validate_record(data: Dict[str, Any]) -> bool:
    required_fields = {"source", "owner", "payload"}
    return all(field in data for field in required_fields) and isinstance(
        data.get("payload"), dict
    )


def _normalize_record(data: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(data["payload"])
    return {
        "record_id": str(uuid.uuid4()),
        "source": str(data["source"]),
        "owner": str(data["owner"]),
        "payload": payload,
        "classification": str(data.get("classification", "confidential")),
        "shared_at": _utc_now(),
        "integrity_status": "verified",
    }


def _read_sample_records() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    if not SAMPLE_FILE.exists():
        return records

    with SAMPLE_FILE.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            event = json.loads(raw)
            records.append(
                _normalize_record(
                    {
                        "source": event["source"],
                        "owner": event["owner"],
                        "payload": {
                            "temperature": event.get("temperature"),
                            "humidity": event.get("humidity"),
                        },
                        "classification": "internal-demo",
                    }
                )
            )
    return records


app = Flask(__name__)
store = RecordStore(RECORDS_FILE)
ledger = SimpleBlockchain(_load_chain())


@app.get("/")
def healthcheck():
    return jsonify(
        {
            "service": "secure-real-time-data-sharing",
            "status": "running",
            "records": store.count(),
            "ledger_valid": ledger.is_valid(),
            "available_endpoints": [
                "/share",
                "/records",
                "/ledger",
                "/ledger/verify",
                "/analytics",
                "/bootstrap",
            ],
        }
    )


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.post("/share")
def share_record():
    payload = request.get_json(silent=True) or {}
    if not _validate_record(payload):
        return (
            jsonify(
                {
                    "error": "Invalid payload. Required fields: source, owner, payload."
                }
            ),
            400,
        )

    stored = _normalize_record(payload)
    store.add(stored)
    block = ledger.add_record(stored)
    _save_chain(ledger)
    return (
        jsonify(
            {
                "message": "Record shared successfully.",
                "record": stored,
                "block": {
                    "index": block.index,
                    "hash": block.hash,
                    "previous_hash": block.previous_hash,
                },
            }
        ),
        201,
    )


@app.post("/bootstrap")
def bootstrap_data():
    if store.count() > 0:
        return jsonify({"message": "Bootstrap skipped because records already exist."})

    records = _read_sample_records()
    if not records:
        return jsonify({"message": "No sample records found."}), 404

    store.extend(records)
    for record in records:
        ledger.add_record(record)
    _save_chain(ledger)

    return jsonify(
        {
            "message": "Sample records loaded successfully.",
            "records_loaded": len(records),
            "ledger_blocks": len(ledger.chain),
        }
    )


@app.get("/records")
def list_records():
    return jsonify({"records": store.all(), "count": store.count()})


@app.get("/analytics")
def record_analytics():
    analytics = store.analytics()
    analytics["ledger_valid"] = ledger.is_valid()
    analytics["ledger_blocks"] = len(ledger.chain)
    return jsonify(analytics)


@app.get("/ledger")
def list_ledger():
    return jsonify({"chain": ledger.to_list()})


@app.get("/ledger/verify")
def verify_ledger():
    return jsonify({"valid": ledger.is_valid(), "blocks": len(ledger.chain)})


if __name__ == "__main__":
    app.run(debug=True)
