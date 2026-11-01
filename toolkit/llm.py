"""OpenAI boundary. No API keys or source content are logged here."""
import socket
import ssl

from openai import (
    OpenAI, AuthenticationError, RateLimitError, APIConnectionError,
    APITimeoutError, APIError, APIStatusError,
)


class GenerationError(Exception):
    pass


def connection_help(exc: Exception) -> str:
    """Classify common connection errors without exposing exception details or secrets."""
    chain = []
    seen = set()
    current = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        chain.append(current)
        current = current.__cause__ or current.__context__
    details = " ".join(str(item).lower() for item in chain)
    if isinstance(exc, APITimeoutError) or any(isinstance(item, TimeoutError) for item in chain) or "timed out" in details:
        return "The connection to OpenAI timed out. Check your network, VPN, firewall, or proxy and try again."
    if any(isinstance(item, ssl.SSLCertVerificationError) for item in chain) or any(term in details for term in ("certificate verify failed", "certificate_verify_failed", "self-signed certificate", "unable to get local issuer certificate")):
        return "TLS certificate verification failed. Check your computer's date and time and whether antivirus or a company proxy is inspecting HTTPS traffic. Ask your network administrator to configure a trusted certificate; do not disable certificate verification."
    if any(isinstance(item, socket.gaierror) for item in chain) or any(term in details for term in ("getaddrinfo failed", "name or service not known", "temporary failure in name resolution", "nodename nor servname")):
        return "Could not resolve the OpenAI server's address. Check your internet connection and DNS settings."
    if "proxy" in details:
        return "Could not connect through the configured proxy. Check your proxy settings or ask your network administrator for help."
    return "Could not connect to OpenAI. A firewall, VPN, proxy, antivirus, or network restriction may be blocking HTTPS access to api.openai.com."


def check_connection() -> tuple[bool, str]:
    """Probe via the same SDK/network configuration, without the user's API key or content."""
    try:
        client = OpenAI(api_key="connection-test-no-real-key", timeout=10, max_retries=0)
        client.models.list()
        return True, "The API server responded. This checks connectivity only, not your key or model access."
    except APIConnectionError as exc:
        return False, connection_help(exc)
    except APIStatusError as exc:
        if exc.status_code == 401:
            return True, "The API server responded (HTTP 401 for the test key). Connectivity works; this does not verify your real key or model access."
        return False, f"The server responded with HTTP {exc.status_code}, but the request was not accepted. A proxy, firewall, or service restriction may be involved."
    except APIError:
        return False, "The API test failed unexpectedly. Check your network and try again."


def generate(api_key: str, system: str, user: str) -> str:
    try:
        client = OpenAI(api_key=api_key, timeout=60, max_retries=1)
        result = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=1800,
        )
        content = result.choices[0].message.content
        if not content or not content.strip():
            raise GenerationError("The model returned an empty response. Please try again.")
        return content.strip()
    except AuthenticationError as exc:
        raise GenerationError("OpenAI rejected this API key. Check the key and try again.") from exc
    except RateLimitError as exc:
        raise GenerationError("OpenAI rate limit or quota reached. Check your usage and billing, then try again.") from exc
    except APIConnectionError as exc:
        raise GenerationError(connection_help(exc)) from exc
    except APIError as exc:
        raise GenerationError("OpenAI couldn't complete the request. Please try again later.") from exc
