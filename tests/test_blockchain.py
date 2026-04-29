import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from backend.blockchain import SimpleBlockchain


def test_new_chain_is_valid():
    chain = SimpleBlockchain()
    assert chain.is_valid() is True


def test_adding_record_keeps_chain_valid():
    chain = SimpleBlockchain()
    chain.add_record(
        {
            "source": "sensor-a",
            "owner": "team-alpha",
            "payload": {"temperature": 28},
        }
    )
    assert chain.is_valid() is True


def test_tampering_breaks_validation():
    chain = SimpleBlockchain()
    chain.add_record(
        {
            "source": "sensor-a",
            "owner": "team-alpha",
            "payload": {"temperature": 28},
        }
    )
    chain.chain[1].record["payload"]["temperature"] = 99
    assert chain.is_valid() is False


def test_chain_can_be_reloaded_from_serialized_data():
    chain = SimpleBlockchain()
    chain.add_record(
        {
            "source": "sensor-z",
            "owner": "team-delta",
            "payload": {"temperature": 24},
        }
    )
    reloaded = SimpleBlockchain(chain.to_list())
    assert reloaded.is_valid() is True
    assert len(reloaded.chain) == 2
