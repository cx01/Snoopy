import utils
import time
import os

limit = 25
os.system('sh badlogins.sh >> badlogins.txt')
logindata = utils.swap('badlogins.txt', True)
blocked = []
for line in logindata:
    data = set(line.split(' '))
    data.pop()

    a = data.pop()
    b = data.pop()
    if len(a.split('.'))>=3:
        addr = a
        count = int(b)
    else:
        count = int(a)
        addr = b
    if count > limit:
        blocked.append(addr)
        print '* %d Connection Attempts made by %s' % (count, addr)
print '\033[1mBlocking These  \033[31m%d\033[0m\033[1m IP Adresses\033[0m' % len(blocked)