#!/usr/bin/env python3
"""Read-only TLS/DNS diagnostics for a hostname; never fetches page content insecurely."""
from __future__ import annotations
import json
import socket
import ssl
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen

def inspect(host: str) -> dict:
    try:
        records = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        return {"host": host, "dns_error": f"{type(exc).__name__}: {exc}", "addresses": []}
    addresses = sorted({record[4][0] for record in records})
    results = []
    for address in addresses:
        item = {"address": address, "family": "IPv6" if ":" in address else "IPv4"}
        try:
            with socket.create_connection((address, 443), timeout=8) as raw:
                context = ssl.create_default_context()
                with context.wrap_socket(raw, server_hostname=host):
                    item["verified_tls"] = True
                    item["verification_error"] = None
        except Exception as exc:
            item["verified_tls"] = False
            item["verification_error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
        # Metadata-only handshake: never fetch or trust page content with this context.
        try:
            diagnostic = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            diagnostic.check_hostname = False
            diagnostic.verify_mode = ssl.CERT_NONE
            with socket.create_connection((address, 443), timeout=8) as raw:
                with diagnostic.wrap_socket(raw, server_hostname=host) as tls:
                    cert = tls.getpeercert()
                    item["certificate_subject"] = cert.get("subject", [])
                    item["certificate_issuer"] = cert.get("issuer", [])
                    item["certificate_not_after"] = cert.get("notAfter")
                    item["certificate_sans"] = [v for k, v in cert.get("subjectAltName", []) if k == "DNS"]
                    item["tls_version"] = tls.version()
        except Exception as exc:
            item["certificate_inspection_error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
        results.append(item)
    return {"host": host, "addresses": results}

def fetch_page(url: str) -> dict:
    try:
        request = Request(url, headers={
            "User-Agent": "OperaLiricoSourceMonitor/1.0",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Encoding": "identity",
        })
        with urlopen(request, timeout=15, context=ssl.create_default_context()) as response:
            body = response.read()
            return {
                "url": url,
                "final_url": response.geturl(),
                "http_status": response.status,
                "bytes": len(body),
                "verified_https": True,
            }
    except Exception as exc:
        return {"url": url, "verified_https": False, "error": f"{type(exc).__name__}: {str(exc)[:240]}"}


def main() -> None:
    hosts = sys.argv[1:] or ["www.tls-belli.it", "tls-belli.it"]
    urls = [
        "https://www.tls-belli.it/bandi_e_avvisi/",
        "https://www.tls-belli.it/concorso-di-canto-2026/",
    ]
    print(json.dumps({
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "note": "All page requests use the default trusted CA store and strict hostname verification. The metadata-only handshake is diagnostic only.",
        "hosts": [inspect(host) for host in hosts],
        "strict_https_page_fetches": [fetch_page(url) for url in urls],
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
