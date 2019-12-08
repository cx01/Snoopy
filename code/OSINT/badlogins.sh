#!/bin/sh
grep "Failed password for" /var/log/auth.log | grep -Po "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" | sort | uniq -c
#EOF
