"""msgspecによる型付きencode/decodeと、atomicなファイル書き込み。

NumPy配列とPathの相互変換hookを含む。
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any, TypeVar, get_origin

import msgspec
import numpy as np
import numpy.typing as npt

_T = TypeVar("_T")
_NumpyArray = npt.NDArray[Any]


@dataclass(frozen=True, slots=True)
class _NumpyArrayPayload:
    dtype: str
    shape: tuple[int, ...]
    data: object

    @classmethod
    def _from_array(cls, array: _NumpyArray) -> _NumpyArrayPayload:
        normalized = np.asarray(array)
        if normalized.dtype.hasobject:
            raise TypeError("NumPy object dtype is not supported")
        return cls(
            dtype=normalized.dtype.str,
            shape=normalized.shape,
            data=normalized.tolist(),
        )

    def _to_array(self) -> _NumpyArray:
        try:
            dtype = np.dtype(self.dtype)
        except TypeError as error:
            raise ValueError(f"invalid NumPy dtype: {self.dtype!r}") from error
        if any(dimension < 0 for dimension in self.shape):
            raise ValueError("NumPy array shape must be non-negative")
        return np.array(self.data, dtype=dtype).reshape(self.shape).copy()


def _encode_hook(value: object) -> object:
    if isinstance(value, np.ndarray):
        return _NumpyArrayPayload._from_array(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"unsupported serialization type: {type(value)!r}")


def _decode_hook(expected_type: Any, value: object) -> object:
    if expected_type is Path:
        if not isinstance(value, str):
            raise TypeError("Path must be decoded from a string")
        return Path(value)
    if expected_type is np.ndarray or get_origin(expected_type) is np.ndarray:
        payload = msgspec.convert(value, type=_NumpyArrayPayload, strict=True)
        return payload._to_array()
    raise TypeError(f"unsupported deserialization type: {expected_type!r}")


class MsgspecIO:
    """Typed JSON, YAML and MessagePack I/O with atomic file writes."""

    _json_encoder = msgspec.json.Encoder(enc_hook=_encode_hook, order="deterministic")
    _msgpack_encoder = msgspec.msgpack.Encoder(
        enc_hook=_encode_hook,
        order="deterministic",
    )

    @classmethod
    def encode_json(cls, value: object) -> str:
        return msgspec.json.format(cls._json_encoder.encode(value), indent=2).decode("utf-8")

    @classmethod
    def decode_json(cls, value: str | bytes, *, type: type[_T]) -> _T:
        return cls._json_decoder(type).decode(value)

    @classmethod
    def write_json(cls, path: Path, value: object) -> Path:
        encoded = msgspec.json.format(cls._json_encoder.encode(value), indent=2) + b"\n"
        return cls._write(path, encoded)

    @classmethod
    def read_json(cls, path: Path, *, type: type[_T]) -> _T:
        return cls._json_decoder(type).decode(path.read_bytes())

    @classmethod
    def write_yaml(cls, path: Path, value: object) -> Path:
        return cls._write(path, msgspec.yaml.encode(value, enc_hook=_encode_hook))

    @classmethod
    def read_yaml(cls, path: Path, *, type: type[_T]) -> _T:
        return cls._yaml_decoder(type)(path.read_bytes())

    @classmethod
    def write_msgpack(cls, path: Path, value: object) -> Path:
        return cls._write(path, cls._msgpack_encoder.encode(value))

    @classmethod
    def read_msgpack(cls, path: Path, *, type: type[_T]) -> _T:
        return cls._msgpack_decoder(type).decode(path.read_bytes())

    @staticmethod
    def _write(path: Path, data: bytes) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=path.parent,
                prefix=f".{path.name}.",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                temporary_file.write(data)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            temporary_path.replace(path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
        return path

    @staticmethod
    @cache
    def _json_decoder(target_type: Any) -> msgspec.json.Decoder[Any]:
        return msgspec.json.Decoder(
            type=target_type,
            dec_hook=_decode_hook,
            strict=True,
        )

    @staticmethod
    @cache
    def _yaml_decoder(target_type: Any) -> Any:
        return lambda data: msgspec.yaml.decode(
            data,
            type=target_type,
            dec_hook=_decode_hook,
            strict=True,
        )

    @staticmethod
    @cache
    def _msgpack_decoder(target_type: Any) -> msgspec.msgpack.Decoder[Any]:
        return msgspec.msgpack.Decoder(
            type=target_type,
            dec_hook=_decode_hook,
            strict=True,
        )
