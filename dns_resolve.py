#!/usr/bin/env python3
"""dns_resolve - DNS record parser and zone file operations."""
import sys
from collections import defaultdict

class DNSRecord:
    def __init__(self, name, rtype, value, ttl=3600):
        self.name = name
        self.rtype = rtype.upper()
        self.value = value
        self.ttl = ttl
    def __repr__(self):
        return f"{self.name} {self.ttl} IN {self.rtype} {self.value}"

class Zone:
    def __init__(self, origin=""):
        self.origin = origin
        self.records = []
    def add(self, name, rtype, value, ttl=3600):
        self.records.append(DNSRecord(name, rtype, value, ttl))
    def query(self, name, rtype=None):
        results = []
        for r in self.records:
            if r.name == name and (rtype is None or r.rtype == rtype.upper()):
                results.append(r)
        return results
    def to_zone_file(self):
        lines = [f"$ORIGIN {self.origin}"] if self.origin else []
        for r in self.records:
            lines.append(str(r))
        return "\n".join(lines)
    @classmethod
    def from_zone_file(cls, text):
        zone = cls()
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith(";"):
                continue
            if line.startswith("$ORIGIN"):
                zone.origin = line.split()[1]
                continue
            parts = line.split()
            if len(parts) >= 5 and parts[2] == "IN":
                zone.add(parts[0], parts[3], " ".join(parts[4:]), int(parts[1]))
        return zone

def resolve_cname(zone, name, rtype="A", depth=10):
    if depth <= 0:
        return []
    records = zone.query(name, rtype)
    if records:
        return records
    cnames = zone.query(name, "CNAME")
    results = []
    for c in cnames:
        results.extend(resolve_cname(zone, c.value, rtype, depth - 1))
    return results

def test():
    z = Zone("example.com.")
    z.add("@", "A", "93.184.216.34")
    z.add("@", "AAAA", "2606:2800:220:1:248:1893:25c8:1946")
    z.add("www", "CNAME", "@")
    z.add("mail", "MX", "10 mail.example.com.")
    assert len(z.query("@", "A")) == 1
    assert z.query("@", "A")[0].value == "93.184.216.34"
    assert len(z.query("mail", "MX")) == 1
    # CNAME resolution
    results = resolve_cname(z, "www", "A")
    assert len(results) == 1 and results[0].value == "93.184.216.34"
    # zone file round-trip
    text = z.to_zone_file()
    z2 = Zone.from_zone_file(text)
    assert len(z2.records) == 4
    assert z2.origin == "example.com."
    print("OK: dns_resolve")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: dns_resolve.py test")
