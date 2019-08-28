from scapy.all import *
import json
import re
import ast

fullstr=''
def sniffOffers(count=20):
    global fullstr
    def callback(pkt):
        global fullstr
        fullstr+=(str(pkt[Raw].load,'utf-8',errors='ignore'))
    def build_lfilter(pkt):
        if ((UDP in pkt) 
        and (pkt[IP].src in albip)
        and ((b'{"' in pkt[Raw].load)
        or (b'"}' in pkt[Raw].load))
        ):
            return True
        else:
            return False
    albip = ['5.188.125.51', '5.188.125.38']
    filthere=' or '.join(x for x in albip)
    sniff(filter='host '+filthere,
            prn=callback, lfilter=build_lfilter, count=count, store=False)
    #a = rdpcap('ah.pcapng')
    #print(a)
    fullstr = re.sub('[^a-zA-z0-9":{},]+','',fullstr)
    fullstr = re.sub(r'3S\^.{0,2}?X','',fullstr)
    find = re.findall('{.*?}',fullstr)
    dictlist=[]
    for obj in find:
        try:
            dictlist.append(json.loads(obj))
        except Exception as e:
            pass 
    return dictlist



if __name__ == '__main__':
    print(sniffOffers())
