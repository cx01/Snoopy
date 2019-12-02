import utils
import time
import os

limit = 25
os.system('sh badlogins.sh >> badlogins.txt')
logindata = utils.swap('badlogins.txt', True)
for line in logindata:
    data = line.replace('\t','').split(' ')
    data = set(data)
    data.remove('')
    try:
        if len(list(data)[0].split('.')) > 2:
            count = list(data)[1]
            addr = list(data)[0]
        else:
            count = list(data)[0]
            addr = list(data)[1]
        print '%s : %d' % (count, addr)
        if count >= limit:
            print '%s has attempted  %d logins ' % (addr, count)
    except:
        pass
        # TODO: blacklist ip
