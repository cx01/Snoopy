import utils
import time
import os

tic = time.time()

def add_drop_rule(addr):
    print '[!!] Dropping all inbound connections from %s' % addr
    drop_cmd = 'iptables -I INPUT -s %s -j DROP' % addr
    os.system(drop_cmd)


def check_logs():
    data_out = {}
    limit = 25
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
            add_drop_rule(addr)
    print '\033[1mBlocking These  \033[31m%d\033[0m\033[1m IP Adresses\033[0m' % len(blocked)
    return blocked, data_out


check_logs()
print '\033[1m\033[32mFINISHED[%ss Elapsed] ' % str(time.time()-tic)