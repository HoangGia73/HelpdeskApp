import io
from pathlib import Path
import zipfile

import pytest

from it_support_suite.backup_manager import BackupRestoreManager
from it_support_suite.safety import validate_removal_target


def test_zip_slip_is_rejected(tmp_path: Path):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("../outside.txt", "unsafe")
    archive.seek(0)
    with zipfile.ZipFile(archive) as source, pytest.raises(ValueError):
        BackupRestoreManager.safe_extract_zip(source, tmp_path / "extract")
    assert not (tmp_path / "outside.txt").exists()


def test_valid_zip_extracts(tmp_path: Path):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("folder/file.txt", "safe")
    archive.seek(0)
    with zipfile.ZipFile(archive) as source:
        BackupRestoreManager.safe_extract_zip(source, tmp_path / "extract")
    assert (tmp_path / "extract/folder/file.txt").read_text() == "safe"


def test_removal_target_must_be_inside_allowed_root(tmp_path: Path):
    allowed = tmp_path / "application-data"
    child = allowed / "cache"
    assert validate_removal_target(str(child), [str(allowed)]) == child.resolve()
    with pytest.raises(ValueError):
        validate_removal_target(str(tmp_path), [str(allowed)])
    with pytest.raises(ValueError):
        validate_removal_target(str(allowed), [str(allowed)])
