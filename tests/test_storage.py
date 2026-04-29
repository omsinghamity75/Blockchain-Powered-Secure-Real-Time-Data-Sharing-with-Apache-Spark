import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from backend.storage import RecordStore


def test_record_store_persists_records(tmp_path: Path):
    store = RecordStore(tmp_path / "records.json")
    store.add(
        {
            "record_id": "1",
            "source": "sensor-a",
            "owner": "team-alpha",
            "payload": {"temperature": 28},
        }
    )

    reloaded = RecordStore(tmp_path / "records.json")
    assert reloaded.count() == 1
    assert reloaded.all()[0]["source"] == "sensor-a"


def test_record_store_analytics(tmp_path: Path):
    store = RecordStore(tmp_path / "records.json")
    store.extend(
        [
            {
                "record_id": "1",
                "source": "sensor-a",
                "owner": "team-alpha",
                "payload": {"temperature": 28},
            },
            {
                "record_id": "2",
                "source": "sensor-b",
                "owner": "team-beta",
                "payload": {"temperature": 34},
            },
        ]
    )

    analytics = store.analytics()
    assert analytics["total_records"] == 2
    assert analytics["owners"]["team-alpha"] == 1
    assert analytics["alert_records"] == 1
