#!/bin/sh
cat ../countrycodes.txt | cut -d ';' -f 2 | while read country; 
do 
	python targets.py target $country
done
# EOF 
