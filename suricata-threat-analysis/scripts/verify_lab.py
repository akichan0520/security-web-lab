#!/usr/bin/env python3
"""Checks the bytes/frames of the packaged synthetic PCAPs, NOT Suricata execution."""
from pathlib import Path
import struct, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'hands-on'/'pcaps'

EXPECTED={
 '01-http-uri.pcap': [(4,b'/wp-content/')],
 '02-rdp-marker.pcap': [(4,b'MS_T120\x00')],
 '03-smb1-marker.pcap': [(4,bytes.fromhex('ff 53 4d 42'))],
 '04-dns-query.pcap': [(1,b'\x08task-001\x08training\x07invalid\x00')],
 '05-http-split.pcap':[(4,b'GET /wp-con'),(6,b'tent/lab-checkin')],
 '06-false-positive.pcap':[(4,b'/wp-content/')],
}

def frames(path):
    data=path.read_bytes()
    assert len(data)>24 and data[:4]==bytes.fromhex('d4 c3 b2 a1')
    off=24; out=[]
    while off<len(data):
        sec,us,cap,orig=struct.unpack_from('<IIII',data,off)
        out.append(data[off+16:off+16+cap]); off+=16+cap
    assert off==len(data)
    return out

def extract_ipv4(packet):
    assert packet[12:14]==b'\x08\x00'
    ihl=(packet[14]&15)*4
    proto=packet[23]
    plen=struct.unpack('!H',packet[16:18])[0]
    body=packet[14+ihl:14+plen]
    if proto==6:
        off=((body[12]>>4)&0xf)*4
        return body[off:]
    if proto==17: return body[8:]
    raise ValueError('unexpected protocol')

def main():
    errors=[]
    for name,checks in EXPECTED.items():
        p=DIR/name
        ff=frames(p)
        for number,needle in checks:
            payload=extract_ipv4(ff[number-1])
            if needle not in payload: errors.append((name,number,'byte mismatch'))
        print('PASS' if not any(e[0]==name for e in errors) else 'FAIL',name,'frames',len(ff),'sha256',hashlib.sha256(p.read_bytes()).hexdigest())
    split=frames(DIR/'05-http-split.pcap')
    combined=extract_ipv4(split[3])+extract_ipv4(split[5])
    assert b'/wp-content/lab-checkin' in combined
    assert not any(b'/wp-content/lab-checkin' in extract_ipv4(x) for x in split)
    if errors:
        print('FAIL:',errors);return 1
    print('All packaged PCAP byte checks passed (Suricata execution NOT checked).')
    return 0

if __name__=='__main__': sys.exit(main())
