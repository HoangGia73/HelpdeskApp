"""Streaming authenticated encryption for backup archives."""
from __future__ import annotations

import os
from pathlib import Path
import struct

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

MAGIC = b"ITSBKP01"
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
CHUNK_SIZE = 1024 * 1024
HEADER = struct.Struct(">8s16s12s")


class BackupDecryptionError(ValueError):
    """Raised when a password is wrong or an archive was modified."""


def _key(password: str, salt: bytes) -> bytes:
    if len(password) < 12:
        raise ValueError("Mật khẩu backup phải có ít nhất 12 ký tự.")
    return Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(
        password.encode("utf-8")
    )


def is_encrypted_backup(path: str | os.PathLike[str]) -> bool:
    try:
        with open(path, "rb") as source:
            return source.read(len(MAGIC)) == MAGIC
    except OSError:
        return False


def encrypt_file(source_path, destination_path, password: str) -> None:
    source_path, destination_path = Path(source_path), Path(destination_path)
    if source_path.resolve() == destination_path.resolve():
        raise ValueError("File nguồn và file mã hóa phải khác nhau.")
    salt, nonce = os.urandom(SALT_SIZE), os.urandom(NONCE_SIZE)
    encryptor = Cipher(algorithms.AES(_key(password, salt)), modes.GCM(nonce)).encryptor()
    partial = destination_path.with_suffix(destination_path.suffix + ".partial")
    try:
        with source_path.open("rb") as source, partial.open("wb") as destination:
            destination.write(HEADER.pack(MAGIC, salt, nonce))
            while chunk := source.read(CHUNK_SIZE):
                destination.write(encryptor.update(chunk))
            destination.write(encryptor.finalize())
            destination.write(encryptor.tag)
            destination.flush()
            os.fsync(destination.fileno())
        os.replace(partial, destination_path)
    finally:
        partial.unlink(missing_ok=True)


def decrypt_file(source_path, destination_path, password: str) -> None:
    source_path, destination_path = Path(source_path), Path(destination_path)
    size = source_path.stat().st_size
    if size < HEADER.size + TAG_SIZE:
        raise BackupDecryptionError("File backup mã hóa không hợp lệ.")
    partial = destination_path.with_suffix(destination_path.suffix + ".partial")
    try:
        with source_path.open("rb") as source:
            magic, salt, nonce = HEADER.unpack(source.read(HEADER.size))
            if magic != MAGIC:
                raise BackupDecryptionError("Không phải định dạng backup mã hóa được hỗ trợ.")
            source.seek(-TAG_SIZE, os.SEEK_END)
            tag = source.read(TAG_SIZE)
            remaining = size - HEADER.size - TAG_SIZE
            source.seek(HEADER.size)
            decryptor = Cipher(
                algorithms.AES(_key(password, salt)), modes.GCM(nonce, tag)
            ).decryptor()
            with partial.open("wb") as destination:
                while remaining:
                    chunk = source.read(min(CHUNK_SIZE, remaining))
                    if not chunk:
                        raise BackupDecryptionError("File backup bị cắt ngắn.")
                    remaining -= len(chunk)
                    destination.write(decryptor.update(chunk))
                try:
                    destination.write(decryptor.finalize())
                except InvalidTag as exc:
                    raise BackupDecryptionError(
                        "Sai mật khẩu hoặc file backup đã bị thay đổi."
                    ) from exc
                destination.flush()
                os.fsync(destination.fileno())
        os.replace(partial, destination_path)
    finally:
        partial.unlink(missing_ok=True)
