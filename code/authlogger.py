import utils
import time
import os

limit = 25
os.system('sh badlogins.sh >> badlogins.txt')
logindata = utils.swap('badlogins.txt', True)
for line in logindata:
    data = line.split(' ')
    data = set(data)
    data.remove('')
    try:
        if len(data[0].split('.'))> 2:
            count = data[1]
            addr = data[0]
        else:
            count = data[0]
            addr = data[1]

        if count >= limit:
            print '%s has attempted  %d logins ' % (addr, count)
    except:
        pass
        # TODO: blacklist ip
