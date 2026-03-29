#!/usr/bin/env python3
"""DNS record types and zone file parser. Zero dependencies."""

RECORD_TYPES = {"A":1,"AAAA":28,"CNAME":5,"MX":15,"NS":2,"TXT":16,"SOA":6,"PTR":12,"SRV":33}

class DNSRecord:
    def __init__(self, name, rtype, value, ttl=3600, priority=None):
        self.name = name; self.rtype = rtype; self.value = value
        self.ttl = ttl; self.priority = priority
    def __repr__(self):
        p = f" {self.priority}" if self.priority is not None else ""
        return f"{self.name} {self.ttl} IN {self.rtype}{p} {self.value}"

class ZoneFile:
    def __init__(self):
        self.records = []; self.origin = ""; self.ttl = 3600

    def add(self, name, rtype, value, ttl=None, priority=None):
        self.records.append(DNSRecord(name, rtype, value, ttl or self.ttl, priority))
        return self

    def lookup(self, name, rtype=None):
        results = []
        for r in self.records:
            if r.name == name and (rtype is None or r.rtype == rtype):
                results.append(r)
        return results

    def to_text(self):
        lines = [f"$ORIGIN {self.origin}" if self.origin else "", f"$TTL {self.ttl}"]
        for r in self.records: lines.append(str(r))
        return "\n".join(l for l in lines if l)

    @classmethod
    def parse(cls, text):
        zone = cls()
        for line in text.split("\n"):
            line = line.strip()
            if not line or line.startswith(";"): continue
            if line.startswith("$ORIGIN"): zone.origin = line.split()[1]; continue
            if line.startswith("$TTL"): zone.ttl = int(line.split()[1]); continue
            parts = line.split()
            if len(parts) >= 4 and parts[2] == "IN":
                name = parts[0]; ttl = int(parts[1]); rtype = parts[3]
                if rtype == "MX" and len(parts)>=6:
                    zone.add(name, rtype, parts[5], ttl, int(parts[4]))
                else:
                    zone.add(name, rtype, " ".join(parts[4:]), ttl)
        return zone

if __name__ == "__main__":
    z = ZoneFile(); z.origin = "example.com."
    z.add("@", "A", "93.184.216.34")
    z.add("www", "CNAME", "example.com.")
    z.add("@", "MX", "mail.example.com.", priority=10)
    print(z.to_text())
