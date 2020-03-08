import utils
import time
import sys
import os


def parse_scan(filename):
    scan = {}
    ports = []
    for line in utils.swap(filename,False):
        try:
            scan['ip'] = line.split(' scan report for ')[1].split(' ')[0]
        except IndexError:
            pass
        try:    # Including Filtered as well
            if ('open' or 'filtered') in line.split(' '):
                ports.append(line.split(' open ')[1].replace(' ', ''))
        except IndexError:
            pass
    scan['open'] = ports
    return scan


def process_scan_data(path, verbose):
    database = {'ssh': [],   'ftp':   [],  'dns': [],  'vnc':   [],
                'irc': [],   'bgp':   [], 'rdp':  [],  'rtsp':  [],
                'upnp': [],  'msrpc': [], 'mysql': [], 'smtp':  [],
                'flask': [], 'telnet': []}
    processed = 0
    start = time.time()
    ssh = 0;    dns = 0
    ftp = 0;    bgp = 0
    vnc = 0;    irc = 0
    rdp = 0;   smtp = 0
    rtsp = 0;  upnp = 0
    mysql = 0; flask = 0
    telnet = 0; msrpc = 0
    for scan_file in os.listdir(path):
        scan_data = parse_scan(path+'/'+scan_file)
        try:
            database[scan_data['ip']] = scan_data
        except KeyError:
            continue
        if 'ssh' in scan_data['open']:
            database['ssh'].append(scan_data['ip'])
            ssh += 1
        if 'ftp' in scan_data['open']:
            database['ftp'].append(scan_data['ip'])
            ftp += 1
        if ('vnc' or 'vnc-1' or 'vnc-2') in scan_data['open']:
            database['vnc'].append(scan_data['ip'])
            vnc += 1
        if 'bgp' in scan_data['open']:
            database['bgp'].append(scan_data['ip'])
            bgp += 1
        if 'dns' in scan_data['open']:
            database['dns'].append(scan_data['ip'])
            dns += 1
        if 'irc' in scan_data['open']:
            database['irc'].append(scan_data['ip'])
            irc += 1
        if 'rdp' in scan_data['open']:
            database['rdp'].append(scan_data['ip'])
            rdp += 1
        if 'upnp' in scan_data['open']:
            database['upnp'].append(scan_data['ip'])
            upnp += 1
        if 'rtsp' in scan_data['open']:
            database['rtsp'].append(scan_data['ip'])
            rtsp += 1
        if 'smtp' in scan_data['open']:
            database['smtp'].append(scan_data['ip'])
            smtp += 1
        if 'mysql' in scan_data['open']:
            database['mysql'].append(scan_data['ip'])
            mysql += 1
        if ('flask' or 'heroku' or 'werkzeug') in scan_data['open']:
            database['flask'].append(scan_data['ip'])
            flask += 1
        if 'msrpc' in scan_data['open']:
            database['msrpc'].append(scan_data['ip'])
            msrpc += 1
        if 'telnet' in scan_data['open']:
            database['telnet'].append(scan_data['ip'])
            telnet += 1
        processed += 1
        if verbose and processed % 50 == 0:
            print '\033[1m\033[32m[*]\033[0m %d Scans Parsed' % processed
    if verbose:
        print '===================================================================='
        print '\033[1m\033[32m[*]\033[0m\033[1m FINISHED \033[31m%ss Elapsed\033[0m\033[1m]' % \
              str(time.time() - start)
        print '\to %d SSH    \tPORTS OPEN' % ssh
        print '\to %d FTP    \tPORTS OPEN' % ftp
        print '\to %d VNC    \tPORTS OPEN' % vnc
        print '\to %d BGP    \tPORTS OPEN' % bgp
        print '\to %d IRC    \tPORTS OPEN' % irc
        print '\to %d DNS    \tPORTS OPEN' % dns
        print '\to %d RDP    \tPORTS OPEN' % rdp
        print '\to %d SMTP   \tPORTS OPEN' % smtp
        print '\to %d UPNP   \tPORTS OPEN' % upnp
        print '\to %d MYSQL  \tPORTS OPEN' % mysql
        print '\to %d FLASK  \tPORTS OPEN' % flask
        print '\to %d MS-RPC \tPORTS OPEN' % msrpc
        print '\to %d TELNET \tPORTS OPEN' % telnet
        print '\033[0m'

    return database


if __name__ == '__main__':
    base = '/home/tylersdurden/Desktop/ScanData'
    n_scans = len(os.listdir(base))
    date, local_time = utils.create_timestamp()

    if ('-q' or 'query') in sys.argv:
        host_data = process_scan_data(base, verbose=False)
        if len(sys.argv) >= 3:
            query = sys.argv[2]
        else:
            query = raw_input('Enter Query:')
        if query in host_data.keys():
            '''
            Return IPs that match the query in a way that will be useful for other scripts 
            IE Print Line by Line, not just a straight print(array)
            '''
            for line in host_data[query]:
                if len(line) > 1:
                    print line
        else:
            print '[!!] Unrecognized Query'
    else:
        print '===================================================================='
        print '|    { NMAP SCAN_DATABASE }    |   %s    |    %s    |' % (date, local_time)
        print '\033[1m\033[32m[*]\033[0m\033[1m %d NMAP Scans Found\033[0m' % n_scans
        host_data = process_scan_data(base, verbose=True)
