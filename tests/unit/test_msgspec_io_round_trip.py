"""MsgspecIOの保存時round-trip検証と3形式の復元を確認するtest。"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from utils.file_io.msgspec_io import MsgspecIO


@dataclass(frozen=True, slots=True)
class _Sample:
    name: str
    values: np.ndarray


def _sample() -> _Sample:
    return _Sample(
        name="sample",
        values=np.arange(6, dtype=np.float64).reshape(2, 3),
    )


def test_write_msgpack_verifies_round_trip_and_restores(tmp_path: Path) -> None:
    path = MsgspecIO.write_msgpack(tmp_path / "state.msgpack", _sample())

    restored = MsgspecIO.read_msgpack(path, type=_Sample)
    assert restored.name == "sample"
    np.testing.assert_array_equal(restored.values, _sample().values)


def test_write_json_verifies_round_trip_and_restores(tmp_path: Path) -> None:
    path = MsgspecIO.write_json(tmp_path / "state.json", _sample())

    restored = MsgspecIO.read_json(path, type=_Sample)
    assert restored.name == "sample"
    np.testing.assert_array_equal(restored.values, _sample().values)


def test_write_yaml_verifies_round_trip_and_restores(tmp_path: Path) -> None:
    path = MsgspecIO.write_yaml(tmp_path / "state.yaml", _sample())

    restored = MsgspecIO.read_yaml(path, type=_Sample)
    assert restored.name == "sample"
    np.testing.assert_array_equal(restored.values, _sample().values)
