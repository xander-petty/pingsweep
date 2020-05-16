"""
This is a beta version of converting pingsweep into a web GUI
"""
__author__ = 'Xander Petty'
__contact__ = 'Alexander.Petty@williams.com'
__version__ = '2.0'

from ipaddress import ip_network, ip_address
from scapy.all import IP, ICMP, sr1
from queue import Queue
from threading import Thread
from flask import Flask, request, render_template
from flask_wtf import FlaskForm 
from wtforms import Label, TextField, validators 
from os import urandom 

app = Flask(__name__)
app.config['DEBUG'] = True 
app.config['SECRET_KEY'] = urandom(24)

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
        data = {
            'ip': ip,
            'ping_count': ping_count,
            'max_threads': max_threads
        }
        print(data)
        ips = [
            '1.1.1.1',
            '1.1.1.2',
            '1.1.1.3',
            '1.1.1.4'
        ]
        return render_template('results.html', ips=ips)

if __name__ == '__main__':
    app.run(ssl_context='adhoc')