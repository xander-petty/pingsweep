"""
This is a beta version of converting pingsweep into a web GUI
"""
__author__ = 'Xander Petty'
__contact__ = 'Alexander.Petty@williams.com'
__version__ = '2.0'

from ipaddress import ip_network, ip_address
from scapy.all import IP, ICMP, sr1
from queue import Queue
from threading import Thread, Lock
from flask import Flask, request, render_template
from flask_wtf import FlaskForm 
from wtforms import Label, TextField, validators 
from os import urandom 
from time import sleep 
# import pyopenssl - Just a commen for building venv

app = Flask(__name__)
app.config['DEBUG'] = True 
app.config['SECRET_KEY'] = urandom(24)

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
        return self.database
    def receive_daemon(self):
        while True:
            packet = self.receive_q.get()
            self.locked_ping(packet)
            self.receive_q.task_done()
    def locked_ping(self, packet):
        print(str(f'Pinging: {packet.dst}'))
        reply = sr1(packet, timeout=2, verbose=False, retry=self.icmp_retry)
        with self.thread_lock:
            if reply != None:
                self.output.append(reply)
            else:
                self.offline.append(ip_address(packet.dst))
    def make_packet(self, ip):
        packet = IP(dst=str(ip), ttl=20)/ICMP()
        self.receive_q.put(packet)
    def receive_input(self):
        for ip in self.output:
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
        # CSV Writer goes here
    def return_results(self):
        self.done = True 
        return self.database

class MainTemplate(FlaskForm):
    ip_label = Label('ip_label', text='IP Address: ')
    ip_entry = TextField(id='ip_entry', validators=[validators.required()])
    ping_count_label = Label('ping_count_label', text='ICMP Retries: ')
    ping_count_entry = TextField(id='ping_count_entry', validators=[validators.required()])
    max_threads_label = Label('max_threads_label', text='Maximum Threads: ')
    max_threads_entry = TextField(id='max_threads_entry', validators=[validators.required()]) 


@app.route('/', methods=['GET', 'POST'])
def main():
    # MAIN FUNCTION
    if request.method == 'GET':
        form = MainTemplate()
        return render_template('main.html', form=form)
    elif request.method == 'POST':
        # TEMPORARY RESULTS:
        ip = request.form['ip_entry']
        ping_count = request.form['ping_count_entry']
        max_threads = request.form['max_threads_entry']
        # results = Pinger(int(ping_count), ip, int(max_threads)).start()
        p = Pinger(int(ping_count), ip, int(max_threads))
        p.start()
        while p.done == False:
            sleep(1)
        results = p.database
        ips = []
        for ip in results:
            if ip['Online'] == True:
                ips.append(ip['IP'])
        # data = {
        #     'ip': ip,
        #     'ping_count': ping_count,
        #     'max_threads': max_threads
        # }
        # print(data)
        # ips = [
        #     '1.1.1.1',
        #     '1.1.1.2',
        #     '1.1.1.3',
        #     '1.1.1.4'
        # ]
        return render_template('results.html', ips=ips)

if __name__ == '__main__':
    app.run(ssl_context='adhoc')