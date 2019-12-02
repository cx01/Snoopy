import utils
import time
import os

tic = time.time()


def add_drop_rule(addr):
    print '[!!] Dropping all inbound connections from %s' % addr
    drop_cmd = 'iptables -I INPUT -s %s -j DROP' % addr
    os.system(drop_cmd)


def check_logs(limit, drop):
    data_out = {}
    os.system('sh badlogins.sh >> badlogins.txt')
    logindata = utils.swap('badlogins.txt', True)
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
    print '\033[1m Blocking These  \033[31m%d\033[0m\033[1m IP Adresses\033[0m' % len(blocked)
    return blocked, data_out


blocked_ips, attempt_counts = check_logs(limit=25, drop=False)
print '\033[1mFINISHED\033[35m[%ss Elapsed] \033[0m' % str(time.time()-tic)
