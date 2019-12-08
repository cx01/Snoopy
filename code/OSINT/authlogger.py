import time
import sys
import os

tic = time.time()


def swap(file_name, destroy):
    data = []
    for line in open(file_name, 'r').readlines():
        data.append(line.replace('\n', ''))
    if destroy:
        os.remove(file_name)
    return data


def add_drop_rule(addr):
    print '[!!] Dropping all inbound connections from %s' % addr
    drop_cmd = 'iptables -I INPUT -s %s -j DROP' % addr
    os.system(drop_cmd)


def check_logs(limit, drop):
    data_out = {}
    os.system('sh badlogins.sh >> badlogins.txt')
    logindata = swap('badlogins.txt', True)
    blocked = []
    for line in logindata:
        data = set(line.split(' '))
        data.pop()

        a = data.pop()
        b = data.pop()
        if len(a.split('.')) >= 3:
            addr = a
            count = int(b)
        else:
            count = int(a)
            addr = b
        data_out[addr] = count
        if count > limit:
            blocked.append(addr)
            print '* %d Connection Attempts made by %s' % (count, addr)
            if drop:
                add_drop_rule(addr)
    print '\033[1m Blocking These  \033[31m%d\033[1m IP Adresses\033[0m' % len(blocked)
    return blocked, data_out


def unique_attempts():
    seen = []
    counts = {}
    os.system('sh badlogins.sh >> jerks.txt')
    for line in swap('jerks.txt', True):
        data = set(line.split(' '))
        data.pop()
        a = data.pop()
        b = data.pop()
        if len(a.split('.')) >= 3:
            addr = a
            count = int(b)
        else:
            count = int(a)
            addr = b
        counts[addr] = count
        seen.append(addr)
    return seen, counts


def dump_unique_addrs(file_out, ip_counts):
    data = ''
    for addr in ip_counts.keys():
        count = ip_counts[addr]
        data += '%s : %d\n' % (addr, count)
    open(file_out, 'w').write(data)
    return True


if 'block' in sys.argv:
    limit = 25
    if '-limit' in sys.argv:
        limit = int(sys.argv[4])
    blocked_ips, attempt_counts = check_logs(limit=25, drop=True)
    print '\033[1mFINISHED\033[32m [%ss Elapsed] \033[0m' % str(time.time() - tic)


if 'dump' in sys.argv:
    data_out = 'unique.txt'
    ip_list, counts = unique_attempts()
    dump_unique_addrs(data_out, counts)
    print '[*] %d Unique IP Addresses have Attempted SSH Logins as root' % len(ip_list)
