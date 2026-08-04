"""Guards for destructive filesystem and network operations."""
from __future__ import annotations

import ipaddress
import os
from pathlib import Path


def validate_ipv4(value: str, *, allow_unspecified: bool = False) -> str:
    address = ipaddress.ip_address(value)
    if address.version != 4 or (address.is_unspecified and not allow_unspecified):
        raise ValueError(f"Địa chỉ IPv4 không hợp lệ: {value}")
    return str(address)


def validate_removal_target(path: str, allowed_roots: list[str]) -> Path:
    """Resolve a deletion target and require it to be below an approved root."""
    if not path or not allowed_roots:
        raise ValueError("Thiếu đường dẫn hoặc phạm vi xóa được phép.")
    target = Path(path).resolve(strict=False)
    anchor = Path(target.anchor)
    if target == anchor or target == Path.home().resolve(strict=False):
        raise ValueError("Từ chối xóa thư mục hệ thống hoặc thư mục người dùng gốc.")
    approved = [Path(root).resolve(strict=False) for root in allowed_roots if root]
    if not any(target != root and os.path.commonpath([target, root]) == str(root) for root in approved):
        raise ValueError(f"Đường dẫn nằm ngoài phạm vi xóa được phép: {target}")
    return target
