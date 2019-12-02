import utils
import time
import os

limit = 25
os.system('sh badlogins.sh >> badlogins.txt')
logindata = utils.swap('badlogins.txt', True)
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
        print '* %d Connection Attempts made by %s' % (count, addr)
print 'Blocking These IP Adresses'