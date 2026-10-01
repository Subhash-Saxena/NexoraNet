from app.core.security import is_authorized_lab_target


def test_authorized_lab_targets():
    """Verify that localhost and private lab subnet targets are strictly allowed."""
    assert is_authorized_lab_target("localhost") is True
    assert is_authorized_lab_target("127.0.0.1") is True
    assert is_authorized_lab_target("::1") is True
    assert (
        is_authorized_lab_target("10.99.1.5", allowed_subnet_cidr="10.99.0.0/16")
        is True
    )
    assert is_authorized_lab_target("gateway.lab.internal") is True


def test_unauthorized_external_targets():
    """Verify that public internet targets and non-lab networks are rejected."""
    # Public IP addresses
    assert is_authorized_lab_target("8.8.8.8") is False
    assert is_authorized_lab_target("1.1.1.1") is False
    assert is_authorized_lab_target("142.250.190.46") is False

    # Arbitrary domain names
    assert is_authorized_lab_target("example.com") is False
    assert is_authorized_lab_target("google.com") is False
    assert is_authorized_lab_target("target.external.org") is False

    # Disallowed private subnets
    assert (
        is_authorized_lab_target("192.168.1.100", allowed_subnet_cidr="10.99.0.0/16")
        is False
    )
