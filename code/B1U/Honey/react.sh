#!/bin/bash
cat $1 | while read n;
 do
  curl -s 'https://ipinfo.io/'$n >> ip.txt
  country=$(cat ip.txt | grep country | cut -d ':' -f 2-4 | cut -d ',' -f 1);
  ip=$(cat ip.txt | grep '"ip": ' | cut -d ':' -f 2 | cut -d ',' -f 1);
  if [ $country != '"US"' ]; then
  	echo 'Country Code is '$country' [NOT USA]'
  	cd ../../R3D
  	ip=${ip//\"} 
  	python targets.py hit $ip
  	cd ../B1U/Honey
  fi
  rm ip.txt
done
#EOF

