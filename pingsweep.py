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
__version__ = '1.6'

from ipaddress import ip_network, ip_address 
from scapy.all import IP, ICMP, sr1 
from pprint import pprint 
from threading import Thread, Lock 
from multiprocessing import Process
from queue import Queue 
from tkinter import font 
import tkinter 
import csv 

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
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)
        # Front-End Setup 
        self.master = master 
        self.master.title("Pingsweep Tool")
        self.grid()
        self.create_widgets()
        # Back-End Setup 
        self.thread_lock = Lock() 
        self.receive_q = Queue()
        self.output = [] 
        self.offline = [] 
        self.online = []
        self.database = []
        self.all_threads = [] 
    def create_widgets(self):
        self.header_label()
        self.network_label()
        self.network_entry()
        self.ping_count_label()
        self.ping_count_entry()
        self.max_threads_label()
        self.max_threads_entry()
        self.file_label()
        self.file_entry()
        self.quit_button()
        self.submit_button()
        self.status_label()
    def header_label(self):
        self.header_label = tkinter.Label(self)
        self.header_label['font'] = font.Font(size=16)
        self.header_label['text'] = str('Multithreaded Ping Tool')
        self.header_label.grid(row=0, column=1, pady=2)
    def network_label(self):
        self.network_label = tkinter.Label(self)
        self.network_label['font'] = font.Font(size=12)
        self.network_label['text'] = str('Enter the network address with CIDR: ')
        self.network_label.grid(row=1, column=0, pady=2)
    def network_entry(self):
        self.network_entry = tkinter.Entry(self)
        self.network_entry['font'] = font.Font(size=12)
        self.network_entry.grid(row=1, column=2, pady=2, padx=2)
    def ping_count_label(self):
        self.ping_count_label = tkinter.Label(self)
        self.ping_count_label['font'] = font.Font(size=12)
        self.ping_count_label['text'] = str('Enter the number of ping retries: ')
        self.ping_count_label.grid(row=2, column=0, pady=2)
    def ping_count_entry(self):
        self.ping_count_entry = tkinter.Entry(self)
        self.ping_count_entry['font'] = font.Font(size=12)
        self.ping_count_entry.grid(row=2, column=2, pady=2, padx=2)
    def max_threads_label(self):
        self.max_threads_label = tkinter.Label(self)
        self.max_threads_label['font'] = font.Font(size=12)
        self.max_threads_label['text'] = str('Enter the maximum number of threads: ')
        self.max_threads_label.grid(row=3, column=0, pady=2)
    def max_threads_entry(self):
        self.max_threads_entry = tkinter.Entry(self)
        self.max_threads_entry['font'] = font.Font(size=12)
        self.max_threads_entry.grid(row=3, column=2, pady=2, padx=2)
    def file_label(self):
        self.file_label = tkinter.Label(self)
        self.file_label['font'] = font.Font(size=12)
        self.file_label['text'] = str('Enter the name of the output file (.csv): ')
        self.file_label.grid(row=4, column=0, pady=2)
    def file_entry(self):
        self.file_entry = tkinter.Entry(self)
        self.file_entry['font'] = font.Font(size=12)
        self.file_entry.grid(row=4, column=2, pady=2, padx=2)
    def quit_button(self):
        self.quit_button = tkinter.Button(self)
        self.quit_button['font'] = font.Font(size=12)
        self.quit_button['text'] = str('QUIT')
        self.quit_button['command'] = self.master.destroy
        self.quit_button.grid(row=10, column=2, pady=2)
    def submit_button(self):
        self.submit_button = tkinter.Button(self)
        self.submit_button['font'] = font.Font(size=12)
        self.submit_button['text'] = str('SUBMIT')
        self.submit_button['command'] = lambda: self.main_function()
        self.submit_button.grid(row=10, column=3, pady=2)
    def status_label(self):
        self.status_label = tkinter.Label(self)
        self.status_label['font'] = font.Font(size=13)
        self.status_label['text'] = str('Status: Not started')
        self.status_label.grid(row=12, column=0, pady=2)
    def make_packet(self, ip):
        packet = IP(dst=str(ip), ttl=20)/ICMP()
        self.receive_q.put(packet)
    def locked_ping(self, packet):
        print(str(f'Pinging: {packet.dst}'))
        reply = sr1(packet, timeout=2, verbose=False, retry=self.retry)
        with self.thread_lock:
        # with thread_lock:
            if reply != None:
                self.output.append(reply)
            else:
                self.offline.append(ip_address(packet.dst))
    def receive_daemon(self):
        while True:
            packet = self.receive_q.get()
            self.locked_ping(packet)
            self.receive_q.task_done() 
    def receive_input(self):
        for ip in self.output:
            self.online.append(ip_address(ip.src))
        self.online = sorted(self.online)
        self.offline = sorted(self.offline)
        # pprint(self.online)
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
        with open(str(self.file_entry.get()), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(self.database[0].keys()))
            writer.writeheader()
            writer.writerows(self.database)
        csvfile.close()
    def main_window(self):
        # Consider clearing the online / offline list - maybe empty que? 
        self.online.clear()
        self.offline.clear()
        self.database.clear()
        self.output.clear()
        self.status_label['bg'] = 'red'
        self.status_label['text'] = 'Status: WORKING'
        self.retry = int(self.ping_count_entry.get())
        all_hosts = list(ip_network(self.network_entry.get()))
        for num in range(int(self.max_threads_entry.get())):
            t = Thread(target=self.receive_daemon)
            t.daemon = True 
            t.start() 
            self.all_threads.append(t)
        for ip in all_hosts:
            self.make_packet(ip)
        self.receive_q.join()
        self.receive_input()
        self.status_label['bg'] = 'green'
        self.status_label['text'] = str('Status: DONE')
        self.results_window()
    def results_window(self):
        row=0
        column=0
        top = tkinter.Toplevel(self)
        top.title(str('Online Devices'))
        top.grid()
        label = tkinter.Label(top)
        label['font'] = font.Font(size=13)
        label['text'] = str('Online Devices')
        label.grid(row=row, column=1)
        row += 1
        labels = []
        for ip in self.online:
            l = tkinter.Label(top)
            l['font'] = font.Font(size=12)
            l['text'] = str(ip)
            l.grid(row=row, column=column, pady=2)
            labels.append(l)
            column += 2
            s = tkinter.Label(top)
            s['font'] = font.Font(size=12)
            s['text'] = str('ONLINE')
            s.grid(row=row, column=column, padx=2, pady=2)
            labels.append(s)
            row += 1
            column -=2

    def main_function(self):
        main_window = Thread(target=self.main_window).start()

master = tkinter.Tk()
window = Application(master)
window.mainloop()
