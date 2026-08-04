import pytest

from it_support_suite.safety import validate_ipv4


@pytest.mark.parametrize("value", ["192.168.1.10", "10.0.0.1", "172.16.2.5"])
def test_valid_ipv4(value):
    assert validate_ipv4(value) == value


@pytest.mark.parametrize("value", ["; shutdown /s", "999.1.1.1", "::1", "0.0.0.0"])
def test_command_injection_and_invalid_addresses_are_rejected(value):
    with pytest.raises(ValueError):
        validate_ipv4(value)
