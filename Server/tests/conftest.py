import pytest


@pytest.fixture
def hostname():
	"""Default hostname for DNS resolution test."""
	return "localhost"
