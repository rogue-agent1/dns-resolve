#!/usr/bin/env python3
"""dns_resolve - DNS lookup."""
import sys,argparse,json,socket,time
def resolve(hostname):
    results={"hostname":hostname}
    try:
        t0=time.time();ip=socket.gethostbyname(hostname);t1=time.time()
        results["ipv4"]=ip;results["resolve_ms"]=round((t1-t0)*1000,2)
    except:results["ipv4"]=None
    try:
        addrs=socket.getaddrinfo(hostname,None)
        results["all_addresses"]=list(set(addr[4][0] for addr in addrs))
        results["address_families"]=list(set(str(addr[0]) for addr in addrs))
    except:pass
    try:results["fqdn"]=socket.getfqdn(hostname)
    except:pass
    try:
        if results.get("ipv4"):results["reverse"]=socket.gethostbyaddr(results["ipv4"])[0]
    except:results["reverse"]=None
    return results
def main():
    p=argparse.ArgumentParser(description="DNS resolver")
    p.add_argument("hostnames",nargs="+")
    args=p.parse_args()
    results=[resolve(h) for h in args.hostnames]
    print(json.dumps({"results":results},indent=2))
if __name__=="__main__":main()
