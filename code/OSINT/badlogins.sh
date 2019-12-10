#!/bin/sh
ls /var/log/auth.log* | while read path; do
    echo $(grep "Failed password for" $path | grep -Po "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" | sort | uniq -c);
done
#EOF
