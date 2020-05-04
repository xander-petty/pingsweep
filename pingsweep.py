"""
This is a scalable thread based ping tool 

Required Modules:
ipaddress
pprint
pythonping
scapy
"""
__author__ = 'Xander Petty'
__contact__ = 'Alexander.Petty@williams.com'
__version__ = '1.4'

from ipaddress import ip_network, ip_address
from scapy.all import IP, ICMP, sr1
from pprint import pprint 
from threading import Thread, Lock 
from queue import Queue 
import sys 
import os 
from time import sleep 
import csv 
import tkinter 
from tkinter import font 

##########################
# network = '192.168.0.0/26'
# ping_count = 4
# max_threads = 100
# network = input('Enter network with CIDR: ')
# ping_count = int(input('Enter the number of ping retries: '))
# max_threads = int(input('Enter the maximum number of threads: '))
# file_name = input('Enter the name of the self.output file (.csv): ')
##########################

class Application(tkinter.Frame):
    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.master = master 
        # self.pack()
        self.grid_rowconfigure(10, weight=1)
        self.grid_columnconfigure(10, weight=1)
        self.grid()
        self.create_widgets() # Calls written function 
        self.thread_lock = Lock()
        self.receive_q = Queue()
        self.output = []
        self.offline = []
        self.all_threads = [] # For debugging purposes. Daemon's close with the process 
    def create_widgets(self):
        self.header()
        self.network_label()
        self.network_entry()
        self.ping_count_label()
        self.ping_count_entry()
        self.max_threads_label()
        self.max_threads_entry()
        self.file_label()
        self.file_entry()
        self.submit()
        self.quit()
    def header(self):
        self.title_object = tkinter.Label(self)
        self.header_font = font.Font()
        self.header_font['size'] = 16
        self.title_object['font'] = self.header_font
        self.title_object['text'] = str('Multithread Ping Tool')
        # self.title_object.anchor = str('top')
        # self.title_object.pack()
        self.title_object.grid(row=0, column=1, pady=2)
    def network_label(self):
        self.network_label = tkinter.Label(self)
        self.network_label['font'] = font.Font(size=12)
        self.network_label['text'] = str('Enter the network address with CIDR: ')
        # self.network_label.pack(side='left')
        # self.network_label.pack()
        self.network_label.grid(row=1, column=0, pady=2)
    def network_entry(self):
        self.network_entry = tkinter.Entry(self)
        self.network_entry['font'] = font.Font(size=12)
        self.network_entry.grid(row=1, column=2, padx=2, pady=2)
    def ping_count_label(self):
        self.ping_count_label = tkinter.Label(self)
        self.ping_count_label['font'] = font.Font(size=12)
        self.ping_count_label['text'] = str('Enter the number of ping retries: ')
        self.ping_count_label.grid(row=2, column=0, pady=2)
    def ping_count_entry(self):
        self.ping_count_entry = tkinter.Entry(self)
        self.ping_count_entry['font'] = font.Font(size=12)
        self.ping_count_entry.grid(row=2, column=2, padx=2, pady=2)
    def max_threads_label(self):
        self.max_threads_label = tkinter.Label(self)
        self.max_threads_label['font'] = font.Font(size=12)
        self.max_threads_label['text'] = str('Enter the maximum number of threads: ')
        self.max_threads_label.grid(row=3, column=0, pady=2)
    def max_threads_entry(self):
        self.max_threads_entry = tkinter.Entry(self)
        self.max_threads_entry['font'] = font.Font(size=12)
        self.max_threads_entry.grid(row=3, column=2, padx=2, pady=2)
    def file_label(self):
        self.file_label = tkinter.Label(self)
        self.file_label['font'] = font.Font(size=12)
        self.file_label['text'] = str('Enter the name of the self.output file (.csv): ')
        self.file_label.grid(row=4, column=0, pady=2)
    def file_entry(self):
        self.file_entry = tkinter.Entry(self)
        self.file_entry['font'] = font.Font(size=12)
        self.file_entry.grid(row=4, column=2, padx=2, pady=2)
    def quit(self):
        self.quit = tkinter.Button(self)
        self.quit['font'] = font.Font(size=12)
        self.quit['text'] = str('QUIT')
        self.quit['command'] = self.master.destroy
        # self.quit.pack(side='bottom')
        self.quit.grid(row=10, column=2, pady=2)
    def submit(self):
        self.submit = tkinter.Button(self)
        self.submit['font'] = font.Font(size=12)
        self.submit['text'] = str('SUBMIT')
        # self.submit['command'] = print(self.network_entry['text'])
        # self.submit['command'] = self.main(self.network_entry['text'], self.max_threads_entry['text'])
        self.submit['command'] = lambda: self.main()
        self.submit.grid(row=10, column=3, pady=2)
    def make_packet(self, ip):
        packet = IP(dst=str(ip), ttl=20)/ICMP()
        self.receive_q.put(packet)
    def locked_ping(self, packet):
        print(str(f'Pinging: {packet.dst}'))
        reply = sr1(packet, timeout=2, verbose=False, retry=int(self.ping_count_entry.get()))
        with self.thread_lock:
            # print(str(f'Pinging: {packet.dst}'))
            if reply != None:
                self.output.append(reply)
            else:
                self.offline.append(ip_address(packet.dst))
    def receive_daemon(self):
        while True:
            packet = self.receive_q.get()
            self.locked_ping(packet)
            self.receive_q.task_done()
    def main(self):
        self.all_hosts = list(ip_network(self.network_entry.get()))
        for num in range(int(self.max_threads_entry.get())):
            t = Thread(target=self.receive_daemon)
            t.daemon = True 
            t.start()
        for ip in self.all_hosts:
            self.make_packet(ip)
        self.receive_q.join()
        self.receive_input()
        self.master.destroy
    def receive_input(self):
        online = []
        for ip in self.output:
            online.append(ip_address(ip.src))
        online = sorted(online)
        self.offline = sorted(self.offline)
        wait = ((len(list(ip_network(self.network_entry.get()))) * 2) / int(self.max_threads_entry.get())) * int(self.ping_count_entry.get())
        # sleep(wait)
        print('#############################################')
        print('###                 ONLINE                ###')
        print('#############################################')
        pprint(online)
        database = []
        for ip in online:
            data = {
                'IP': str(ip),
                'Online': True
            }
            database.append(data)
        for ip in self.offline:
            data = {
                'IP': str(ip),
                'Online': False
            }
            database.append(data)
        # Adding to CSV File 
        with open(self.file_entry.get(), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(database[0].keys()))
            writer.writeheader()
            writer.writerows(database)
        csvfile.close()

# main(network, max_threads)
root = tkinter.Tk()
window = Application(master=root)
window.mainloop()
