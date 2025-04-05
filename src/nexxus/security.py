import hashlib
import hmac
from abc import ABC, abstractmethod

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse

from nexxus.models import Blacklist

# Blacklisted IPs and Hostnames
BLACKLISTED_IPS = {"192.168.1.100", "2001:db8::ff00:42:8329"}
BLACKLISTED_HOSTNAMES = {"banned.example.com"}
API_SECRET_KEY = b"supersecurekey"


class SecurityCheck(ABC):
    """Abstract base class for security checks."""

    @abstractmethod
    def validate(self, request: HttpRequest) -> HttpResponse | None:
        """Perform a security check. Return HttpResponse if check fails, otherwise None."""


class IPBlacklistCheck(SecurityCheck):
    """Check if the request comes from a blacklisted IP."""

    def get_client_ip(self, request: HttpRequest) -> str | bool:
        """Extract the client's IP address from the HTTP request."""
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        ip_address = ip.split(",")[0].strip() if ip else request.META.get("REMOTE_ADDR")
        return Blacklist.objects.filter(ip_address=ip_address).exists()

    def validate(self, request: HttpRequest) -> HttpResponse | None:
        """Validate the incoming request by checking if the client's IP address is blacklisted."""
        ip = self.get_client_ip(request)
        if ip:
            return HttpResponse("Forbidden: Blacklisted IP", status=403)
        return None


class HostnameBlacklistCheck(SecurityCheck):
    """Check if the request comes from a blacklisted hostname."""

    def validate(self, request: HttpRequest) -> HttpResponse | None:
        """Check if the request originates from a blacklisted hostname."""
        hostname = request.META.get("HTTP_HOST", "")
        if Blacklist.objects.filter(hostname=hostname).exists():
            return HttpResponse("Forbidden: Blacklisted Hostname", status=403)
        return None


class APIKeyCheck(SecurityCheck):
    """Ensure the request includes a valid API key."""

    def validate(self, request: HttpRequest) -> HttpResponse | None:
        """Validate the presence and correctness of the API key in the request headers."""
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != settings.EXPECTED_API_KEY:
            return HttpResponse("Unauthorized: Invalid API Key", status=401)
        return None


class HMACSignatureCheck(SecurityCheck):
    """Verify the HMAC signature for request integrity."""

    def validate(self, request: HttpRequest) -> HttpResponse | None:
        """Validate the HMAC (Hash-based Message Authentication Code) signature included in the request headers."""
        signature = request.headers.get("X-Signature")
        if not signature:
            return HttpResponse("Unauthorized: Missing Signature", status=401)

        expected_hmac = hmac.new(API_SECRET_KEY, request.body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_hmac):
            return HttpResponse("Unauthorized: Invalid Signature", status=401)
        return None


class RateLimitCheck(SecurityCheck):
    """Apply rate limiting to prevent abuse."""

    def get_client_ip(self, request: HttpRequest) -> HttpResponse | None:
        """Retrieve the IP address of the client from the HTTP request."""
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        return ip.split(",")[0].strip() if ip else request.META.get("REMOTE_ADDR")

    def validate(self, request: HttpRequest) -> HttpResponse | None:
        """Validate the incoming request against the rate limiting policy."""
        client_ip = self.get_client_ip(request)
        cache_key = f"rate_limit_{client_ip}"
        request_count = cache.get(cache_key, 0)

        if request_count > settings.LEGACY_REQUESTS_PER_MINUTE:
            return HttpResponse("Too Many Requests", status=429)

        cache.set(cache_key, request_count + 1, timeout=60)
        return None
