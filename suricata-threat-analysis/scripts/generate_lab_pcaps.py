#!/usr/bin/env python3
"""Deterministic SAFE network lab captures. Standard library only.
No exploits, no executable payload, no Internet traffic. Reproducible PCAP files.
All IPs are TEST-NET or documentation ranges (RFC 5737).
"""
from pathlib import Path
import socket, struct, json, hashlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'hands-on'/'pcaps'
OUT.mkdir(parents=True, exist_ok=True)
MAC_A = bytes.fromhex('020000000011')
MAC_B = bytes.fromhex('020000000022')
TIME = 1792070000  # fixed lab time, not an incident timestamp


def checksum(data):
    if len(data) & 1: data += b'\0'
    words = struct.unpack('!%dH' % (len(data)//2), data)
    n = sum(words)
    while n >> 16: n=(n & 0xffff)+(n>>16)
    return (~n) & 0xffff

def ethernet(src, dst, data):
    return dst + src + struct.pack('!H', 0x0800) + data

def ipv4(src, dst, proto, payload, ident):
    a,b = socket.inet_aton(src),socket.inet_aton(dst)
    hdr = struct.pack('!BBHHHBBH4s4s',0x45,0,20+len(payload),ident,0x4000,64,proto,0,a,b)
    hdr=hdr[:10]+struct.pack('!H',checksum(hdr))+hdr[12:]
    return hdr+payload

def tcp(src,dst,sp,dp,seq,ack,flags,payload=b''):
    sh=struct.pack('!HHIIHHHH',sp,dp,seq,ack,(5<<12)|flags,64240,0,0)
    pseudo=socket.inet_aton(src)+socket.inet_aton(dst)+struct.pack('!BBH',0,6,len(sh)+len(payload))
    cs=checksum(pseudo+sh+payload)
    return sh[:16]+struct.pack('!H',cs)+sh[18:]+payload

def udp(src,dst,sp,dp,payload):
    sh=struct.pack('!HHHH',sp,dp,8+len(payload),0)
    pseudo=socket.inet_aton(src)+socket.inet_aton(dst)+struct.pack('!BBH',0,17,len(sh)+len(payload))
    cs=checksum(pseudo+sh+payload)
    return sh[:6]+struct.pack('!H',cs or 0xffff)+payload

def pcap_write(name,packets):
    path=OUT/name
    with path.open('wb') as f:
        f.write(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1))
        for i,p in enumerate(packets):
            f.write(struct.pack('<IIII',TIME+i,i*1000,len(p),len(p)))
            f.write(p)
    return path

class PacketFlow:
    def __init__(self,src,dst,sp,dp):
        self.src,self.dst,self.sp,self.dp=src,dst,sp,dp
        self.cs,self.ss=1000,5000
        self.pk=[]
        self.ident=1
    def emit(self,client,flags,data=b''):
        s,d,sp,dp=(self.src,self.dst,self.sp,self.dp) if client else (self.dst,self.src,self.dp,self.sp)
        seq,ack=(self.cs,self.ss) if client else (self.ss,self.cs)
        seg=tcp(s,d,sp,dp,seq,ack,flags,data)
        pkt=ethernet(MAC_A if client else MAC_B, MAC_B if client else MAC_A,ipv4(s,d,6,seg,self.ident))
        self.pk.append(pkt)
        self.ident+=1
        # SYN / FIN count as one sequence byte
        delta=len(data)+(1 if flags&0x02 else 0)+(1 if flags&0x01 else 0)
        if client: self.cs+=delta
        else: self.ss+=delta
    def handshake(self):
        self.emit(True,0x02)
        self.emit(False,0x12)
        self.emit(True,0x10)
        return self
    def request(self,data):
        self.emit(True,0x18,data)
        self.emit(False,0x10)
        return self
    def response(self,data):
        self.emit(False,0x18,data)
        self.emit(True,0x10)
        return self

HTTP_RESPONSE=(b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK')

def req(uri):
    return ('GET '+uri+' HTTP/1.1\r\nHost: training.invalid\r\nUser-Agent: LabReader/1.0\r\nConnection: close\r\n\r\n').encode()

def make_http_good():
    f=PacketFlow('192.0.2.10','198.51.100.20',51514,80).handshake().request(req('/wp-content/lab-checkin')).response(HTTP_RESPONSE)
    return pcap_write('01-http-uri.pcap',f.pk)

def make_rdp():
    # TPKT-shaped opaque training payload: NOT a real RDP exploitation packet.
    body=b'\x02\xf0\x80'+b'LAB_DEMONSTRATION='+b'MS_T120\x00'+b'NO_EXPLOIT'
    pkt=b'\x03\x00'+struct.pack('!H',4+len(body))+body
    f=PacketFlow('192.0.2.21','198.51.100.33',51521,3389).handshake().request(pkt)
    return pcap_write('02-rdp-marker.pcap',f.pk)

def make_smb():
    # Illustrative NetBIOS + SMB1 signature; NOT an actual SMB negotiate/exploit.
    p=b'\xffSMB'+b'\x72'+b'LAB_SIMULATION_ONLY'+b'\x00'*8
    nb=b'\x00'+len(p).to_bytes(3,'big')+p
    f=PacketFlow('192.0.2.31','198.51.100.44',51531,445).handshake().request(nb)
    return pcap_write('03-smb1-marker.pcap',f.pk)

def dns_query(name,ident):
    parts=name.split('.')
    q=b''.join(bytes([len(p)])+p.encode('ascii') for p in parts)+b'\x00'
    return struct.pack('!HHHHHH',ident,0x0100,1,0,0,0)+q+struct.pack('!HH',1,1)

def make_dns():
    s,d='192.0.2.41','198.51.100.53'
    a=dns_query('task-001.training.invalid',0x4242)
    b=dns_query('www.training.invalid',0x4243)
    packs=[]
    for ident,p,sp in ((1,a,53241),(2,b,53242)):
        packs.append(ethernet(MAC_A,MAC_B,ipv4(s,d,17,udp(s,d,sp,53,p),ident)))
    return pcap_write('04-dns-query.pcap',packs)

def make_split():
    f=PacketFlow('192.0.2.51','198.51.100.20',51551,80).handshake()
    f.request(b'GET /wp-con')
    f.request(b'tent/lab-checkin HTTP/1.1\r\nHost: training.invalid\r\nConnection: close\r\n\r\n')
    f.response(HTTP_RESPONSE)
    return pcap_write('05-http-split.pcap',f.pk)

def make_fp():
    f=PacketFlow('192.0.2.61','198.51.100.20',51561,80).handshake()
    f.request(req('/wp-content/images/normal.jpg'))
    f.response(HTTP_RESPONSE)
    return pcap_write('06-false-positive.pcap',f.pk)

if __name__=='__main__':
    paths=[func() for func in (make_http_good,make_rdp,make_smb,make_dns,make_split,make_fp)]
    manifest=[]
    for path in paths:
        data=path.read_bytes()
        n=0; off=24
        while off<len(data):
            ts,us,cap,orig=struct.unpack_from('<IIII',data,off)
            n+=1; off+=16+cap
        assert off==len(data)
        manifest.append({'pcap':path.name,'sha256':hashlib.sha256(data).hexdigest(),'frames':n,'bytes':len(data)})
    (ROOT/'hands-on'/'answers'/'pcap-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for m in manifest: print(m['pcap'],m['frames'],m['sha256'])
