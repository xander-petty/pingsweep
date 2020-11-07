"""
This is a version of pingsweep that is able to run exclusively
from the shell
"""
__author__ = 'Xander Petty'
__contact__ = 'xander12093@me.com'
__version__ = '0.1'

from ipaddress import ip_network, ip_address
from scapy.all import IP, ICMP, sr1
from queue import Queue
from threading import Thread, Lock
from time import sleep
import argparse


class Pinger():
    def __init__(self, icmp_retry, network, max_threads):
        self.done = False
        self.icmp_retry = icmp_retry
        self.network = network
        self.max_threads = max_threads
        self.online = []
        self.offline = []
        self.database = []
        self.output = []
        self.thread_lock = Lock()
        self.receive_q = Queue()
        self.all_threads = []

    def start(self):
        self.online.clear()
        self.offline.clear()
        self.database.clear()
        self.output.clear()
        all_hosts = list(ip_network(self.network))
        if len(self.all_threads) <= 255:
            for num in range(int(self.max_threads)):
                t = Thread(target=self.receive_daemon)
                t.daemon = True
                t.start()
                self.all_threads.append(t)
        for ip in all_hosts:
            self.make_packet(ip)
        self.receive_q.join()
        self.receive_input()
        self.done = True
        # print(self.database)

    def receive_daemon(self):
        while True:
            packet = self.receive_q.get()
            self.locked_ping(packet)
            self.receive_q.task_done()

    def locked_ping(self, packet):
        # print(str(f'Pinging: {packet.dst}'))
        params = {
            'x': packet,
            'timeout': 2,
            'verbose': False,
            'retry': int(self.icmp_retry)
        }
        reply = sr1(**params)
        with self.thread_lock:
            if reply is not None:
                self.output.append(reply)
            else:
                self.offline.append(ip_address(packet.dst))

    def make_packet(self, ip):
        packet = IP(dst=str(ip), ttl=20)/ICMP()
        self.receive_q.put(packet)

    def receive_input(self):
        for ip in self.output:
            self.online.append(ip_address(ip.src))
        self.online = sorted(self.online)
        self.offline = sorted(self.offline)
        for ip in self.online:
            data = {
                'IP': str(ip),
                'Online': True
            }
            self.database.append(data)
        for ip in self.offline:
            data = {
                'IP': str(ip),
                'Online': False
            }
            self.database.append(data)

    def return_results(self):
        self.done = True
        return self.database


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pingsweep')
    parser.usage = '%(prog)s [args]'
    parser.description = 'Pings all entries in CIDR range'
    parser.add_argument('--retries', help='Retry attempts on packet')
    parser.add_argument('--maxthreads', help='Max concurrent pings')
    parser.add_argument('--network', help='Network and CIDR')
    args = parser.parse_args()
    # network = input('Enter network address in CIDR format: ')
    # retry = input('How many retry packets?: ')
    # max_threads = input('Enter maximum number of concurrent threads: ')
    # params = {
    #     'network': network,
    #     'icmp_retry': retry,
    #     'max_threads': max_threads
    # }
    params = {
        'network': args.network,
        'icmp_retry': args.retries,
        'max_threads': args.maxthreads
    }
    pinger = Pinger(**params)
    pinger.start()
    while pinger.done is False:
        sleep(1)
    results = pinger.database
    online_ips = []
    offline_ips = []
    for ip in results:
        if ip['Online'] is True:
            online_ips.append(ip['IP'])
        elif ip['Online'] is False:
            offline_ips.append(ip['IP'])
    print('ONLINE')
    for ip in online_ips:
        print(ip)
