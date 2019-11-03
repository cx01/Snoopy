from threading import Thread
import binascii
import socket
import struct
import time
import sys
import os

tic = time.time()
known_ports = [20, 21, 22, 23, 25, 50, 51, 53, 67, 68, 69, 80,
               110, 119, 123, 135, 136, 137, 138, 139, 143, 153,
               161, 162, 389, 443, 3389, 5900, 8001, 8009, 8002,
               8080, 8082, 8443]

port_names = {20: 'ftp', 21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
              50: 'IPSec', 51: 'IPSec', 53: 'DNS', 67: 'DHCP', 68: 'DHCP',
              69: 'TFTP', 80: 'HTTP', 110:'POP3', 119: 'NNTP', 123: 'NTP',
              135: 'NetBIOS', 136: 'NetBIOS', 137: 'NetBIOS', 138: 'NetBIOS',
              139: 'NetBIOS', 143: 'IMAP', 153: 'SGMP', 161:'SNMP', 162: 'SNMP', 1190: 'STUN',
              1901: 'Fujitsu ICL Terminal Emulator Program A', 1902: 'Fujitsu ICL Terminal Emulator Program B',
              389: 'LDAP', 443: 'SSL', 4000: 'ICQ Data Port', 3389: 'RDP', 5900:'RFB 00.500',
              8001: 'VCOM Tunnel', 8002: 'ORDBMS', 8009:'ajp13', 8080: 'HTTP-Proxy', 8082: 'black-ice',
              8443: 'HTTPS-Proxy'}


def discover_niface():
    cmd = 'iwconfig | grep ESSID >> nx.txt;clear'
    os.system(cmd)
    iface = swap('nx.txt', True).pop().split(' ')[0]
    return iface


def swap(file_name, destroy):
    data = []
    for line in open(file_name,'r').readlines():
        data.append(line.replace('\n', ''))
    if destroy:
        os.remove(file_name)
    return data


def raw_sock_connect(target, port):
    hostname = ''
    reply = ''
    opened = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((target, port))
        opened = True
        hostname = socket.gethostbyaddr(s.getpeername()[0])[0]
        print '%s : %s' % (s.getpeername()[0] ,hostname)
        reply = s.recv(1024).replace('\n', '').replace('\t', '')
    except socket.error:
        s.close()
    s.close()
    return opened, reply, hostname


def quick_scan(remote_host):
    scan = {}
    peer = ''
    for port in known_ports:
        isOpen, status, remote = raw_sock_connect(remote_host, port)
        if len(list(remote)) > 1:
            peer = remote
        if isOpen:
            if status == '':
                if port in port_names.keys():
                    status = port_names[port]
                else:
                    status = 'Unknown Protocol'
            print '[*] Port \033[1m%d is \033[32mopen\033[0m (%s)' % (port, str(status))
        scan[port] = status
    return scan, peer


def full_scan(remote_host):
    name = ''
    scan = {}
    ports = range(20, 9999)
    for port in ports:
        isOpen, status, remote = raw_sock_connect(remote_host, port)
        if len(list(remote)) > 1:
            name = remote
        if isOpen:
            if status == '':
                if port in port_names.keys():
                    status = port_names[port]
                else:
                    status = 'Unknown Protocol'

            print '[*] Port \033[1m%d is \033[32mopen\033[0m (%s)' % (port, str(status))
        scan[port] = status
    return scan, name


def lan_host_enum(timeOut):
    # iface = discover_niface()
    rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
    hosts = []
    pkts = []
    print '\033[1m~ Sniffing the LAN for Active Hosts ~\033[0m'
    while time.time()-tic < timeOut:

        ''' pings might help enumerate quiet hosts? '''
        packet = rawSocket.recvfrom(2048)
        ethernet_header = packet[0][0:14]
        arp_header = packet[0][14:42]
        ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)
        arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)

        ethertype = ethernet_detailed[2]
        if ethertype != '\x08\x06':         # skip non-ARP packets
            continue

        dmac = binascii.hexlify(ethernet_detailed[0])
        smac = binascii.hexlify(ethernet_detailed[1])
        hdwr = binascii.hexlify(arp_detailed[0])
        prot = binascii.hexlify(arp_detailed[1])
        hwsz = binascii.hexlify(arp_detailed[2])
        proz = binascii.hexlify(arp_detailed[3])
        opcd = binascii.hexlify(arp_detailed[4])
        hsmc = binascii.hexlify(arp_detailed[5])
        hsip = socket.inet_ntoa(arp_detailed[6])
        hdmc = binascii.hexlify(arp_detailed[7])
        hdip = socket.inet_ntoa(arp_detailed[8])
        # print "Dest MAC:        ", dmac
        # print "Source MAC:      ", smac
        # print "Type:            ", binascii.hexlify(ethertype)
        # print "Hardware type:   ", hdwr
        # print "Protocol type:   ", prot
        # print "Hardware size:   ", hwsz
        # print "Protocol size:   ", proz
        # print "Opcode:          ", opcd
        # print "Source MAC:      ", hsmc
        # print "Source IP:       ", hsip
        # print "Dest MAC:        ", hdmc
        # print "Dest IP:         ", hdip
        if hsip not in set(hosts):
            print '\033[1m[-] \033[32m%s\033[0m' % hsip
        hosts.append(hsip)
    if '0.0.0.0' in hosts:
        hosts.remove('0.0.0.0')
    return set(hosts), pkts


if '-scan' in sys.argv:
    host = sys.argv[2]
    print '\033[1mScanning \033[3m\033[35m%s\033[0m' % host
    if ('-f' or '--fast') not in sys.argv:
        scan, host_name = full_scan(host)
    else:
        scan, host_name,  = quick_scan(host)
    print host_name

if '-lan' in sys.argv:
    if os.getuid() != 0:
        print '\033[1m[*] \033[31mYou Must be Root to Run this Option!!\033[0m'
        exit()
    unique_ips, packets = lan_host_enum(30)
    print '\033[31m%d\033[0m Unique IPs Seen\033[0m' % len(unique_ips)

if 'curious' in sys.argv:
    unique_ips, packets = lan_host_enum(15)
    print '\033[31m%d\033[0m Unique IPs Seen\033[0m' % len(unique_ips)
    for addr in unique_ips:
        print '\033[1m== \033[34mScanning %s\033[0m\033[1m ==\033[0m' % addr
        try:
            scan_data, host_name = quick_scan(addr)
            if host_name != '':
                print '\033[1m== Finished Scanning \033[33m%s\033[0m\033[1m ==\033[0m' % host_name
            else:
                print '\033[1m== Finished Scanning %s ==\033[0m' % addr
            if scan_data[135] or scan_data[139]:
                print '\033[1mEXPLOITING SMB \033[31mCVE 2010-2351\033[0m' \
                      '\033[1m Against %s\033[0m' % addr
                os.system('python smbreak.py %s' % addr)
        except KeyboardInterrupt:
            pass
print 'FINISHED [%ss Elapsed]' % str(time.time()-tic)





