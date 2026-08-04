from pathlib import Path

import pytest

from it_support_suite.backup_crypto import (
    BackupDecryptionError, decrypt_file, encrypt_file, is_encrypted_backup,
)


def test_encrypted_backup_round_trip(tmp_path: Path):
    source = tmp_path / "backup.zip"
    encrypted = tmp_path / "backup.itsbackup"
    restored = tmp_path / "restored.zip"
    source.write_bytes((b"commercial-backup-data\0" * 100_000) + b"end")
    encrypt_file(source, encrypted, "a-strong-password-123")
    assert is_encrypted_backup(encrypted)
    assert encrypted.read_bytes() != source.read_bytes()
    decrypt_file(encrypted, restored, "a-strong-password-123")
    assert restored.read_bytes() == source.read_bytes()


def test_wrong_password_never_leaves_plaintext(tmp_path: Path):
    source = tmp_path / "backup.zip"
    encrypted = tmp_path / "backup.itsbackup"
    restored = tmp_path / "restored.zip"
    source.write_bytes(b"sensitive")
    encrypt_file(source, encrypted, "correct-password-123")
    with pytest.raises(BackupDecryptionError):
        decrypt_file(encrypted, restored, "incorrect-password")
    assert not restored.exists()
    assert not (tmp_path / "restored.zip.partial").exists()


def test_tampered_backup_is_rejected(tmp_path: Path):
    source = tmp_path / "backup.zip"
    encrypted = tmp_path / "backup.itsbackup"
    source.write_bytes(b"sensitive")
    encrypt_file(source, encrypted, "correct-password-123")
    data = bytearray(encrypted.read_bytes())
    data[-20] ^= 1
    encrypted.write_bytes(data)
    with pytest.raises(BackupDecryptionError):
        decrypt_file(encrypted, tmp_path / "out.zip", "correct-password-123")
