import utils
import time
import os

limit = 25
os.system('sh badlogins.sh >> badlogins.txt')
logindata = utils.swap('badlogins.txt', True)
for line in logindata:
    data = set(line.split(' '))
    try:
        data.remove('')
        count = int(data[0])
        addr = data[1]
    except:
        pass
    if count >= limit:
        print '%s has attempted  %d logins ' % (addr, count)
        # TODO: blacklist ip