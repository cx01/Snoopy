import sys
import os


def swap(file_name, destroy):
    data = []
    for line in open(file_name, 'rb').readlines():
        data.append(line.replace('\n', ''))
    if destroy:
        os.remove(file_name)
    return data


def arr2str(array):
    content = ''
    for ln in array:
        content += ln + '\n'
    return content


if __name__ == '__main__':
    file_in = ''
    if len(sys.argv) >=2:
        file_in = sys.argv[1]
    if os.path.isfile(file_in):
        print '[*] Parsing %s' % file_in

    raw_data = swap(file_in, False)
    addresses = []
    for line in raw_data:
        try:
            addresses.append(line.split(' to ')[1])
        except IndexError:
            pass
    print '[*] %d IP Addresses Found ' % len(addresses)
    open('parsed_%s' % file_in, 'wb').write(arr2str(addresses))

    # Find Locations (If file is too large, you'll go over the API Limit!
    os.system('bash react.sh')
