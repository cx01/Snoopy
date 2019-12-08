#!/bin/sh

if [ $# != 1 ]; then
    echo 'Incorrect Usage!'
    echo '$ ./close_port <port> '
    exit
fi

sudo iptables -I INPUT -s $1 -j DROP
# EOF
