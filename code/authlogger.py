from threading import Thread
import time
import os

def swap(file_name, destroy):
    data = []
    for line in open(file_name,'r').readlines():
        data.append(line.replace('\n', ''))
    if destroy:
        os.remove(file_name)
    return data


cmd = 'echo $(grep "Failed password for" /var/log/auth.log | grep -Po "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" ' \
      '| sort | uniq -c)'
os.system(cmd+' >> login_counter.txt')
ip_counts = {}
for line in swap('login_counter.txt', False):
    data = set(line.split(' '))
    try:
        data.remove('')
    except KeyError:
        continue
    count = int(data[0])
    addr = int(data[1])
    if count > 30:
        print '%s has attempted to login %d time. Adding to BlockList' % (addr, count)