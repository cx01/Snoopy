#!/bin/sh

ls /var/log/auth.log* | while read fname; 
do
    fext=$(file $fname | cut -d':' -f2);
    if [ "$fext" = " ASCII text" ]; then
        echo " [*] Logging Unique IPs from "$fname" log file"
        grep "Failed password for" $fname | grep -Po "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" | sort | uniq -c >> log.txt 
    else
        echo '[*] Moving '$fname' to current folder for archiving'
        mv $fname $PWD
    fi
done
#EOF

