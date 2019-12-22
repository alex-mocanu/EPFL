#!/bin/bash

docker exec attacker /bin/bash -c 'iptables -t nat -A POSTROUTING -j MASQUERADE'
docker exec attacker /bin/bash -c 'iptables -A FORWARD -s 172.16.0.2 -p tcp --dport 443 -j NFQUEUE --queue-num 1'
