from dns_resolve import DNSRecord, ZoneFile, RECORD_TYPES
z = ZoneFile(); z.origin = "example.com."
z.add("@", "A", "1.2.3.4")
z.add("www", "CNAME", "example.com.")
z.add("@", "MX", "mail.example.com.", priority=10)
assert len(z.records) == 3
a_recs = z.lookup("@", "A")
assert len(a_recs) == 1 and a_recs[0].value == "1.2.3.4"
mx_recs = z.lookup("@", "MX")
assert mx_recs[0].priority == 10
text = z.to_text()
assert "1.2.3.4" in text
assert RECORD_TYPES["A"] == 1
assert RECORD_TYPES["MX"] == 15
print("dns_resolve tests passed")
