#!/usr/bin/env python3
"""DNS resolver — recursive resolution simulator."""
import sys, random

ZONE_DB = {
    ".": {"com": "198.41.0.4", "org": "199.7.83.42", "net": "192.5.6.30"},
    "com": {"example": "93.184.216.34", "google": "216.58.214.206"},
    "example.com": {"www": "93.184.216.34", "mail": "93.184.216.35", "api": "93.184.216.36"},
    "google.com": {"www": "142.250.80.46", "mail": "142.250.80.47"},
}

class DNSResolver:
    def __init__(self):
        self.cache = {}; self.queries = 0
    def resolve(self, domain, verbose=True):
        if domain in self.cache:
            if verbose: print(f"  [cache] {domain} -> {self.cache[domain]}")
            return self.cache[domain]
        parts = domain.split(".")
        self.queries += 1
        if verbose: print(f"  Query root for '{parts[-1]}'")
        tld = parts[-1]
        if tld not in ZONE_DB.get(".", {}):
            return f"NXDOMAIN: {domain}"
        zone = f"{parts[-2]}.{tld}" if len(parts) > 1 else tld
        self.queries += 1
        if verbose: print(f"  Query TLD '{tld}' for '{zone}'")
        if zone in ZONE_DB:
            host = parts[0] if len(parts) > 2 else parts[0]
            if host in ZONE_DB[zone]:
                ip = ZONE_DB[zone][host]
                self.cache[domain] = ip
                if verbose: print(f"  [auth] {domain} -> {ip}")
                return ip
        return f"NXDOMAIN: {domain}"

if __name__ == "__main__":
    domains = sys.argv[1:] or ["www.example.com", "mail.example.com", "www.google.com", "www.example.com", "unknown.xyz"]
    r = DNSResolver()
    for d in domains:
        print(f"\nResolving {d}:")
        result = r.resolve(d)
        print(f"  Result: {result}")
    print(f"\nTotal queries: {r.queries}, Cache entries: {len(r.cache)}")
