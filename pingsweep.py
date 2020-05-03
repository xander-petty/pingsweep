"""
This is a test of building a multithreaded ping tool with
manual packet crafting and thread daemons
"""
__author__ = 'Xander Petty'
__contact__ = 'Alexander.Petty@williams.com'
__version__ = '1.0'

from ipaddress import ip_network, ip_address
from scapy.all import IP, ICMP, sr1
from pprint import pprint 
from threading import Thread, Lock 
from queue import Queue 
import sys 
import os 
from time import sleep 

thread_lock = Lock()
receive_q = Queue()
output = []
all_threads = [] # For debugging purposes. Daemon's close with the process 

##########################
# network = '192.168.0.0/26'
# ping_count = 4
# max_threads = 100
network = input('Enter network with CIDR: ')
ping_count = int(input('Enter the number of ping retries: '))
max_threads = int(input('Enter the maximum number of threads: '))
##########################

def make_packet(ip):
    packet = IP(dst=str(ip), ttl=20)/ICMP()
    receive_q.put(packet)

def locked_ping(packet):
    print(str(f'Pinging: {packet.dst}'))
    reply = sr1(packet, timeout=2, verbose=False, retry=ping_count)
    with thread_lock:
        # print(str(f'Pinging: {packet.dst}'))
        if reply != None:
            output.append(reply)

def receive_daemon():
    while True:
        packet = receive_q.get()
        locked_ping(packet)
        receive_q.task_done()

def main(network, max_threads):
    all_hosts = list(ip_network(network))
    for num in range(max_threads):
        t = Thread(target=receive_daemon)
        t.daemon = True 
        t.start()
    for ip in all_hosts:
        make_packet(ip)
    receive_q.join()


main(network, max_threads)

online = []
for ip in output:
    online.append(ip_address(ip.src))
online = sorted(online)
wait = ((len(list(ip_network(network))) * 2) / max_threads) * ping_count
# sleep(wait)
print('#############################################')
print('###                 ONLINE                ###')
print('#############################################')
pprint(online)
