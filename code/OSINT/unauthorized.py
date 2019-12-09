import matplotlib.pyplot as plt
import numpy as np
import random
import time
import sys
import os


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


def pull_rogue_ip_list():
    counter = {}
    for line in swap('unique.txt', False):
        ip = line.split(' : ')[0]
        login_attempts = line.split(' : ')[1]
        counter[ip] = int(login_attempts)
    return list(set(counter.keys())), counter


def load_countries():
    codes = {}
    for line in swap('../countrycodes.txt', False):
        country_name = line.split(';')[0]
        country_code = line.split(';')[1]
        codes[country_code] = country_name
    return codes


def determine_login_locales(unique):
    tic = time.time()
    log = False
    if not os.path.isfile('locales.txt'):
        log = True
        content = ''
    country_codes = load_countries()
    unknowns = []
    countries = {}
    counts = dict()
    for country in country_codes:
        counts[country_codes[country]] = 0
    for ip_addr in unique:
        try:
            found = False
            country = cmd('whois %s | grep country:' % ip_addr).pop().split('country:')[1]
            for e in country.split(' '):
                if (e or e.upper()) in country_codes.keys():
                    country = country_codes[e]
                    found = True
            if not found:
                print 'Unknown WHOIS country Entry: %s' % country
            else:
                countries[ip_addr] = country
                counts[country] += 1
            if log and found:
                content += '%s : %s\n' % (ip_addr, country)
        except IndexError:
            pass
    if log:
        open('locales.txt', 'w').write(content)
        print '=== FINISHED Looking Up %d Unique IPs [%ss Elapsed] ===' % \
              (len(unique), str(time.time() - tic))
    return countries, counts, unknowns


def retrieve_unauthorized_origins():
    tic = time.time()
    country_codes = load_countries()
    counts = {}
    countries = {}
    unique = 0
    for country, code in country_codes.iteritems():
        counts[code] = 0
    if os.path.isfile('locales.txt'):
        for line in swap('locales.txt', False):
            ip = line.split(' : ')[0]
            country = line.split(' : ')[1]
            counts[country] += 1
            countries[ip] = country
            unique += 1
    else:
        print '[!!] Locales file Missing!'
        exit()
    print '=== FINISHED Retrieving %d IP Locations [%ss Elapsed] ===' % \
          (unique, str(time.time() - tic))
    return countries, counts, country_codes


def compute_stats(counts):
    percents = {}
    total = np.array(counts.values()).sum()
    for country in country_counts.keys():
        if country_counts[country] > 0:
            percents[country] = np.round((100 * country_counts[country]) / total)
    return percents


unique_ips, login_attempts = pull_rogue_ip_list()
if not os.path.isfile('locales.txt') or 'update_locations' in sys.argv:
    ip_origins, country_counts, unknown = determine_login_locales(unique_ips)
else:
    ip_origins, country_counts, codes = retrieve_unauthorized_origins()
ip_percentiles = compute_stats(country_counts)
print '[*] %d Countries Identified' % len(country_counts.keys())


if 'plot' in sys.argv:
    f, ax = plt.subplots()
    ii = 0
    included = []
    for pct in ip_percentiles.values():
        if pct > 1:
            place = ip_percentiles.keys()[ii]
            plt.bar(ii, pct, label=place)
            included.append(place)
        ii += 1
    plt.title('Unauthorized SSH Attempts by Country')
    plt.ylabel('% of  Unauthorized Login Attempts')
    plt.legend(included)
    # plt.setp(included, rotation=40, ha="right")
    plt.show()


