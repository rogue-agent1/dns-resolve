#!/usr/bin/env python3
"""DNS record parser and resolver (using socket/struct, no dnspython)."""
import sys, socket, struct, random

def build_query(domain, qtype=1):
    tid = random.randint(0, 65535)
    header = struct.pack(">HHHHHH", tid, 0x0100, 1, 0, 0, 0)
    question = b""
    for label in domain.split("."):
        question += bytes([len(label)]) + label.encode()
    question += b"\x00" + struct.pack(">HH", qtype, 1)
    return header + question, tid

def parse_response(data):
    tid, flags, qdcount, ancount, _, _ = struct.unpack(">HHHHHH", data[:12])
    offset = 12
    for _ in range(qdcount):
        while data[offset] != 0:
            if data[offset] & 0xC0 == 0xC0: offset += 2; break
            offset += data[offset] + 1
        else:
            offset += 1
        offset += 4
    records = []
    for _ in range(ancount):
        if data[offset] & 0xC0 == 0xC0: offset += 2
        else:
            while data[offset] != 0: offset += data[offset] + 1
            offset += 1
        rtype, rclass, ttl, rdlength = struct.unpack(">HHIH", data[offset:offset+10])
        offset += 10
        rdata = data[offset:offset+rdlength]
        if rtype == 1 and rdlength == 4:
            records.append({"type": "A", "ttl": ttl, "value": socket.inet_ntoa(rdata)})
        elif rtype == 28 and rdlength == 16:
            records.append({"type": "AAAA", "ttl": ttl, "value": socket.inet_ntop(socket.AF_INET6, rdata)})
        else:
            records.append({"type": rtype, "ttl": ttl, "value": rdata.hex()})
        offset += rdlength
    return records

def resolve(domain, server="8.8.8.8", qtype=1, timeout=3):
    query, tid = build_query(domain, qtype)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(query, (server, 53))
        data, _ = sock.recvfrom(4096)
        return parse_response(data)
    finally:
        sock.close()

def test():
    q, tid = build_query("example.com")
    assert len(q) > 12
    assert 0 <= tid <= 65535
    # Parse a minimal crafted response
    header = struct.pack(">HHHHHH", tid, 0x8180, 1, 1, 0, 0)
    question = b"\x07example\x03com\x00" + struct.pack(">HH", 1, 1)
    answer = b"\xc0\x0c" + struct.pack(">HHIH", 1, 1, 300, 4) + socket.inet_aton("93.184.216.34")
    records = parse_response(header + question + answer)
    assert len(records) == 1
    assert records[0]["type"] == "A"
    assert records[0]["value"] == "93.184.216.34"
    print("  dns_resolve: ALL TESTS PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else:
        domain = sys.argv[2] if len(sys.argv) > 2 else "example.com"
        for r in resolve(domain): print(f"{r['type']}: {r['value']} (TTL: {r['ttl']})")
