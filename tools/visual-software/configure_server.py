#!/usr/bin/env python3
"""Embed only public server configuration; never print keys or credentials."""
import base64
import ipaddress
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]


def endpoint(value, name):
    value = value.strip()
    if not value:
        raise ValueError(f"{name} is required")
    if any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError(f"{name} must be a host or host:port")
    parsed = urlsplit("//" + value)
    if parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise ValueError(f"{name} must not contain credentials, a scheme or a path")
    host = parsed.hostname or ""
    try:
        ipaddress.ip_address(host)
    except ValueError:
        labels = host.rstrip(".").split(".")
        if len(host) > 253 or not all(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", s) for s in labels):
            raise ValueError(f"{name} contains an invalid hostname") from None
    if parsed.port is not None and not 1 <= parsed.port <= 65535:
        raise ValueError(f"{name} contains an invalid port")
    return value


def read_config(env):
    host = endpoint(env.get("RENDEZVOUS_SERVER", ""), "RENDEZVOUS_SERVER")
    key = env.get("RS_PUB_KEY", "").strip()
    try:
        valid_key = len(base64.b64decode(key, validate=True)) == 32
    except ValueError:
        valid_key = False
    if not valid_key:
        raise ValueError("RS_PUB_KEY must be the base64-encoded 32-byte PUBLIC server key")
    relay = env.get("RELAY_SERVER", "").strip()
    if relay:
        relay = endpoint(relay, "RELAY_SERVER")
    api = env.get("API_SERVER", "").strip()
    if api:
        url = urlsplit(api)
        if (url.scheme not in ("https", "http") or not url.hostname
                or url.username or url.password or url.query or url.fragment
                or any(c.isspace() or ord(c) < 32 for c in api)):
            raise ValueError("API_SERVER must be an HTTP(S) URL without credentials")
    return [("custom-rendezvous-server", host), ("key", key),
            ("relay-server", relay), ("api-server", api)]


def rust_string(value):
    # All accepted input is ASCII; quote explicitly for Rust string syntax.
    if not value.isascii():
        raise ValueError("Server values must use ASCII (punycode for international domains)")
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def render(config):
    pairs = "\n".join(f"    ({rust_string(k)}, {rust_string(v)})," for k, v in config)
    return "// Generated public server settings. Do not commit.\nconst SERVER_DEFAULTS: &[(&str, &str)] = &[\n" + pairs + "\n];\n"


def main():
    try:
        source = render(read_config(os.environ))
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    (ROOT / "src/visual_software_server.rs").write_text(source, encoding="utf-8")
    print("Visual Software server configuration validated and embedded (values hidden).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
