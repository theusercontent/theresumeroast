import socket
import ssl
import unittest
from unittest.mock import patch

import httpx
from openai import APIConnectionError, APITimeoutError, AuthenticationError

from toolkit.llm import check_connection, connection_help


class ConnectionTests(unittest.TestCase):
    def test_certificate_message_does_not_expose_exception(self):
        try:
            try:
                raise ssl.SSLCertVerificationError("CERTIFICATE_VERIFY_FAILED secret-value")
            except ssl.SSLCertVerificationError as cause:
                raise APIConnectionError(request=httpx.Request("GET", "https://api.openai.com")) from cause
        except APIConnectionError as exc:
            result = connection_help(exc)
        self.assertIn("certificate", result.lower())
        self.assertNotIn("secret-value", result)
        self.assertIn("do not disable", result.lower())

    def test_dns_and_timeout(self):
        self.assertIn("resolve", connection_help(socket.gaierror("getaddrinfo failed")))
        self.assertIn("timed out", connection_help(APITimeoutError(request=httpx.Request("GET", "https://api.openai.com"))))

    @patch("toolkit.llm.OpenAI")
    def test_probe_uses_dummy_key_and_treats_401_as_connectivity(self, openai):
        response = httpx.Response(401, request=httpx.Request("GET", "https://api.openai.com/v1/models"))
        openai.return_value.models.list.side_effect = AuthenticationError("unauthorized", response=response, body=None)
        ok, message = check_connection()
        self.assertTrue(ok)
        self.assertIn("does not verify", message)
        self.assertEqual(openai.call_args.kwargs["api_key"], "connection-test-no-real-key")
        self.assertEqual(openai.call_args.kwargs["max_retries"], 0)

    @patch("toolkit.llm.OpenAI")
    def test_probe_reports_connection_failure(self, openai):
        openai.return_value.models.list.side_effect = APIConnectionError(request=httpx.Request("GET", "https://api.openai.com"))
        ok, message = check_connection()
        self.assertFalse(ok)
        self.assertIn("Could not connect", message)


if __name__ == "__main__":
    unittest.main()
