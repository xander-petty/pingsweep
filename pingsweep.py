"""
This is a scalable thread based ping tool 

Required Modules:
ipaddress
pprint
pythonping
"""
__author__ = 'Xander Petty'
__contact__ = 'Alexander.Petty@williams.com'
__version__ = '1.0'

from ipaddress import ip_network
from pythonping import ping 
from threading import Thread, Lock 
from queue import Queue 
from pprint import pprint 

thread_lock = Lock()
q = Queue()

def locked_ping(ip, count):
    test = ping(ip, count=count)
    with thread_lock:
        results = {
            'IP': ip,
            'Online': test.success()
        }
        pprint(results)

def variable_map(ip_list, ping_count):
    mapped = []
    for ip in ip_list:
        mapped.append([str(ip), ping_count])
    return mapped

def thread_task():
    while True: # Used as daemon 
        ip, count = q.get()
        locked_ping(ip, count)
        q.task_done() 

def main(network, ping_count, max_threads):
    ip_list = list(ip_network(network))
    mapped = variable_map(ip_list, ping_count)
    for t in range(max_threads):
        thread = Thread(target=thread_task)
        thread.daemon = True 
        thread.start() 
    for ping_set in mapped:
        q.put(ping_set)
    q.join() 


network = input('Please enter a network and cidr pair: ')
count = int(input('How many pings each?: '))
max_threads = int(input('What is the maximum thread count?: '))
# network = '192.168.0.0/27'
# count = 4 
# max_threads = 40

main(network, count, max_threads)
