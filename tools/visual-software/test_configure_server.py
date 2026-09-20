import base64
import unittest
from configure_server import read_config, render


class ServerConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.env = {"RENDEZVOUS_SERVER": "support.example.com:21116",
                    "RS_PUB_KEY": base64.b64encode(bytes(range(32))).decode()}

    def test_valid_configuration_and_optional_values(self):
        self.env.update(RELAY_SERVER="relay.example.com:21117", API_SERVER="https://api.example.com")
        values = dict(read_config(self.env))
        self.assertEqual(values["custom-rendezvous-server"], self.env["RENDEZVOUS_SERVER"])
        self.assertEqual(values["key"], self.env["RS_PUB_KEY"])
        self.assertIn('("relay-server", "relay.example.com:21117")', render(values.items()))

    def test_no_fallback_when_required_settings_are_missing(self):
        for key in self.env:
            with self.subTest(key=key), self.assertRaises(ValueError):
                read_config({k:v for k,v in self.env.items() if k != key})

    def test_invalid_keys_are_rejected(self):
        for key in ["", "not base64", base64.b64encode(b"too short").decode(), base64.b64encode(bytes(64)).decode()]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                read_config(dict(self.env, RS_PUB_KEY=key))

    def test_hosts_cannot_inject_code_or_credentials(self):
        for host in ['https://example.com', 'user:password@example.com', 'example.com/path',
                     'example.com\nmalicious', 'example.com?x=1', 'example.com:99999',
                     'example.com:0', 'bad_host', 'example.com"; code()']:
            with self.subTest(host=host), self.assertRaises(ValueError):
                read_config(dict(self.env, RENDEZVOUS_SERVER=host))

    def test_ipv4_and_ipv6(self):
        for host in ['192.0.2.1', '[2001:db8::1]:21116']:
            with self.subTest(host=host):
                self.assertEqual(dict(read_config(dict(self.env, RENDEZVOUS_SERVER=host)))["custom-rendezvous-server"], host)

    def test_api_rejects_credentials_and_non_http_urls(self):
        for api in ['file:///etc/passwd', 'https://user:password@example.com', 'https://example.com?token=x']:
            with self.subTest(api=api), self.assertRaises(ValueError):
                read_config(dict(self.env, API_SERVER=api))


if __name__ == '__main__':
    unittest.main()
