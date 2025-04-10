import hashlib
import hmac

import pytest
from django.conf import Settings
from django.http import HttpRequest
from django.test import Client
from faker import Faker
from pytest_mock import MockerFixture

from nexxus.models import Blacklist
from nexxus.security import (
    APIKeyCheck,
    HMACSignatureCheck,
    HostnameBlacklistCheck,
    IPBlacklistCheck,
)


@pytest.fixture
def client() -> Client:
    """Django test client fixture."""
    return Client()


@pytest.fixture
def fake() -> Faker:
    """Faker fixture."""
    return Faker()


@pytest.fixture
def mock_request(mocker: MockerFixture) -> HttpRequest:
    """Mock HttpRequest."""
    request = mocker.create_autospec(HttpRequest, instance=True)
    request.META = {}
    request.headers = {}
    request.body = b""
    return request


@pytest.mark.django_db
class TestIPBlacklistCheck:
    """Test IP Blacklist Check."""

    def test_blacklisted_ip(self, mock_request: HttpRequest, mocker: MockerFixture) -> None:
        """Test blacklisted IP."""
        mock_request.META["REMOTE_ADDR"] = "192.168.1.100"
        mocker.patch.object(Blacklist.objects, "filter", return_value=mocker.Mock(exists=lambda: True))
        response = IPBlacklistCheck().validate(mock_request)
        assert response is not None
        assert response.status_code == 403
        assert response.content == b"Forbidden: Blacklisted IP"

    def test_allowed_ip(self, mock_request: HttpRequest, mocker: MockerFixture) -> None:
        """Test allowed IP."""
        mock_request.META["REMOTE_ADDR"] = "192.168.1.101"
        mocker.patch.object(Blacklist.objects, "filter", return_value=mocker.Mock(exists=lambda: False))
        response = IPBlacklistCheck().validate(mock_request)
        assert response is None


@pytest.mark.django_db
class TestHostnameBlacklistCheck:
    """Test Hostname Blacklist Check."""

    def test_blacklisted_hostname(self, mock_request: HttpRequest, mocker: MockerFixture) -> None:
        """Test blacklisted hostname."""
        mock_request.META["HTTP_HOST"] = "banned.example.com"
        mocker.patch.object(Blacklist.objects, "filter", return_value=mocker.Mock(exists=lambda: True))
        response = HostnameBlacklistCheck().validate(mock_request)
        assert response is not None
        assert response.status_code == 403
        assert response.content == b"Forbidden: Blacklisted Hostname"

    def test_allowed_hostname(self, mock_request: HttpRequest, mocker: MockerFixture) -> None:
        """Test allowed hostname."""
        mock_request.META["HTTP_HOST"] = "allowed.example.com"
        mocker.patch.object(Blacklist.objects, "filter", return_value=mocker.Mock(exists=lambda: False))
        response = HostnameBlacklistCheck().validate(mock_request)
        assert response is None


class TestAPIKeyCheck:
    """Test API Key Check."""

    def test_valid_key(self, mock_request: HttpRequest, settings: Settings) -> None:
        """Test valid API key."""
        settings.EXPECTED_API_KEY = "valid_api_key"
        mock_request.headers["X-API-Key"] = "valid_api_key"
        response = APIKeyCheck().validate(mock_request)
        assert response is None

    def test_invalid_key(self, mock_request: HttpRequest, settings: Settings) -> None:
        """Test invalid API key."""
        settings.EXPECTED_API_KEY = "valid_api_key"
        mock_request.headers["X-API-Key"] = "invalid_api_key"
        response = APIKeyCheck().validate(mock_request)
        assert response.status_code == 401
        assert response.content == b"Unauthorized: Invalid API Key"

    def test_missing_key(self, mock_request: HttpRequest, settings: Settings) -> None:
        """Test missing API key."""
        settings.EXPECTED_API_KEY = "valid_api_key"
        response = APIKeyCheck().validate(mock_request)
        assert response.status_code == 401
        assert response.content == b"Unauthorized: Invalid API Key"


class TestHMACSignatureCheck:
    """Test HMAC Signature Check."""

    def test_valid_signature(self, mock_request: HttpRequest) -> None:
        """Test valid HMAC signature."""
        mock_request.body = b"test body"
        signature = hmac.new(b"supersecurekey", mock_request.body, hashlib.sha256).hexdigest()
        mock_request.headers["X-Signature"] = signature
        response = HMACSignatureCheck().validate(mock_request)
        assert response is None

    def test_invalid_signature(self, mock_request: HttpRequest) -> None:
        """Test invalid HMAC signature."""
        mock_request.body = b"test body"
        mock_request.headers["X-Signature"] = "invalid_signature"
        response = HMACSignatureCheck().validate(mock_request)
        assert response is not None
        assert response.status_code == 401
        assert response.content == b"Unauthorized: Invalid Signature"

    def test_missing_signature(self, mock_request: HttpRequest) -> None:
        """Test missing HMAC signature."""
        response = HMACSignatureCheck().validate(mock_request)
        assert response is not None
        assert response.status_code == 401
        assert response.content == b"Unauthorized: Missing Signature"
