import ipaddress
import socket
import urllib.parse
from typing import Tuple

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # RFC 1918 Private
    ipaddress.ip_network("172.16.0.0/12"),    # RFC 1918 Private
    ipaddress.ip_network("192.168.0.0/16"),   # RFC 1918 Private
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local (AWS/cloud metadata 169.254.169.254)
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
    ipaddress.ip_network("0.0.0.0/8"),        # Current network
]

ALLOWED_SCHEMES = {"http", "https"}

def validate_public_url(url: str) -> Tuple[bool, str]:
    """
    Validates that a URL is a legitimate public web target and defends against SSRF
    (Server-Side Request Forgery) attacks targeting local/internal resources or cloud metadata.
    """
    if not url or not isinstance(url, str):
        return False, "URL cannot be empty."

    url = url.strip()
    try:
        parsed = urllib.parse.urlsplit(url)
    except Exception as e:
        return False, f"Malformed URL format: {str(e)}"

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False, f"Prohibited URL scheme '{parsed.scheme}'. Only http and https are allowed."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL must include a valid hostname."

    # Reject localhost or common internal names
    hostname_lower = hostname.lower()
    if hostname_lower in {"localhost", "127.0.0.1", "::1", "metadata.google.internal", "instance-data"}:
        return False, "Access to localhost or internal metadata targets is forbidden."

    # Resolve IP addresses and inspect for private/link-local ranges
    try:
        addr_infos = socket.getaddrinfo(hostname, None)
        for addr in addr_infos:
            ip_str = addr[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            for blocked_net in BLOCKED_IP_NETWORKS:
                if ip_obj in blocked_net:
                    return False, f"Target hostname resolves to a restricted or private address range ({ip_str})."
    except socket.gaierror:
        # Host might not resolve or might be offline
        return False, f"Could not resolve domain name '{hostname}'. Please check spelling or connectivity."
    except Exception as e:
        return False, f"Security verification error: {str(e)}"

    return True, ""
