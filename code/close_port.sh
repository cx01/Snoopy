#!/bin/sh

if [ $# != 1 ]; then
    echo 'Incorrect Usage!'
    echo '$ ./close_port <port> '
    exit
fi

sudo iptables -A INPUT -p tcp --dport $1 -m state --state NEW,ESTABLISHED -j REJECT