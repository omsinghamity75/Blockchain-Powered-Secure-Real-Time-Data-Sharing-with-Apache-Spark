import hashlib
import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


@dataclass
class Block:
    index: int
    timestamp: float
    record: Dict[str, Any]
    previous_hash: str
    hash: str


class SimpleBlockchain:
    def __init__(self, chain_data: List[Dict[str, Any]] | None = None) -> None:
        if chain_data:
            self.chain = [Block(**block) for block in chain_data]
        else:
            self.chain: List[Block] = [self._create_genesis_block()]

    def _create_genesis_block(self) -> Block:
        record = {"type": "genesis", "message": "initial block"}
        block_hash = self._calculate_hash(0, 0.0, record, "0")
        return Block(
            index=0,
            timestamp=0.0,
            record=record,
            previous_hash="0",
            hash=block_hash,
        )

    def _calculate_hash(
        self, index: int, timestamp: float, record: Dict[str, Any], previous_hash: str
    ) -> str:
        payload = json.dumps(
            {
                "index": index,
                "timestamp": timestamp,
                "record": record,
                "previous_hash": previous_hash,
            },
            sort_keys=True,
        )
        return _sha256(payload)

    def add_record(self, record: Dict[str, Any]) -> Block:
        previous = self.chain[-1]
        timestamp = time.time()
        index = previous.index + 1
        block_hash = self._calculate_hash(index, timestamp, record, previous.hash)
        block = Block(
            index=index,
            timestamp=timestamp,
            record=record,
            previous_hash=previous.hash,
            hash=block_hash,
        )
        self.chain.append(block)
        return block

    def is_valid(self) -> bool:
        for index in range(1, len(self.chain)):
            current = self.chain[index]
            previous = self.chain[index - 1]
            expected_hash = self._calculate_hash(
                current.index,
                current.timestamp,
                current.record,
                current.previous_hash,
            )
            if current.hash != expected_hash:
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def to_list(self) -> List[Dict[str, Any]]:
        return [asdict(block) for block in self.chain]
