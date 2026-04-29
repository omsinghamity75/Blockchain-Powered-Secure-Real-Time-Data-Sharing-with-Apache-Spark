import json
from pathlib import Path
from typing import Any, Dict, List


class RecordStore:
    def __init__(self, storage_path: str | Path) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._records: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            self._records = []
            return

        with self.storage_path.open("r", encoding="utf-8") as handle:
            self._records = json.load(handle)

    def _save(self) -> None:
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(self._records, handle, indent=2)

    def add(self, record: Dict[str, Any]) -> Dict[str, Any]:
        self._records.append(record)
        self._save()
        return record

    def extend(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self._records.extend(records)
        self._save()
        return records

    def all(self) -> List[Dict[str, Any]]:
        return list(self._records)

    def count(self) -> int:
        return len(self._records)

    def analytics(self) -> Dict[str, Any]:
        records = self._records
        total = len(records)
        owners: Dict[str, int] = {}
        sources: Dict[str, int] = {}
        alert_records = 0

        for record in records:
            owner = str(record.get("owner", "unknown"))
            source = str(record.get("source", "unknown"))
            owners[owner] = owners.get(owner, 0) + 1
            sources[source] = sources.get(source, 0) + 1

            payload = record.get("payload", {})
            temperature = payload.get("temperature")
            if isinstance(temperature, (int, float)) and temperature >= 32:
                alert_records += 1

        return {
            "total_records": total,
            "owners": owners,
            "sources": sources,
            "alert_records": alert_records,
        }
