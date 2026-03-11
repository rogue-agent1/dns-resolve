#!/usr/bin/env python3
"""DNS resolver (builds raw UDP queries)."""
import sys, socket, struct, random
def build_query(domain, qtype=1):
    tid=random.randint(0,65535)
    header=struct.pack('>HHHHHH',tid,0x0100,1,0,0,0)
    question=b''
    for part in domain.split('.'): question+=bytes([len(part)])+part.encode()
    question+=b'\x00'+struct.pack('>HH',qtype,1)
    return header+question,tid
def parse_response(data):
    tid,flags,qdcount,ancount=struct.unpack('>HHHH',data[:8])
    offset=12
    for _ in range(qdcount):
        while data[offset]!=0:
            if data[offset]&0xc0==0xc0: offset+=2; break
            offset+=data[offset]+1
        else: offset+=1
        offset+=4
    answers=[]
    for _ in range(ancount):
        if data[offset]&0xc0==0xc0: offset+=2
        else:
            while data[offset]!=0: offset+=data[offset]+1
            offset+=1
        atype,aclass,ttl,rdlen=struct.unpack('>HHIH',data[offset:offset+10]); offset+=10
        if atype==1 and rdlen==4:
            answers.append('.'.join(str(b) for b in data[offset:offset+rdlen]))
        offset+=rdlen
    return answers
domain=sys.argv[1] if len(sys.argv)>1 else 'example.com'
server=sys.argv[2] if len(sys.argv)>2 else '8.8.8.8'
query,tid=build_query(domain)
sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.settimeout(3); sock.sendto(query,(server,53))
data,_=sock.recvfrom(512)
answers=parse_response(data)
print(f"DNS query: {domain} @{server}")
for a in answers: print(f"  A: {a}")
if not answers: print("  (no A records)")
