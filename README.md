# Snoopy 
This project is my first foray into experimenting with security on the public internet. Some of 
these tools will have a Blue Team feel, and others might have a Red Team feel.

## Installation
Install the repository with `git clone https://github.com/scott-robbins/Snoopy`

## Usage
To discover active hosts on the lan and see what ports are open just run `python utils.py curious`
![](https://raw.githubusercontent.com/scott-robbins/Snoopy/master/resources/example_discovery.png)

For more targeted scans, you scan run somethig like the following `python utils.py -scan <IP Address>`
![Scan](https://raw.githubusercontent.com/scott-robbins/Snoopy/master/resources/ex_scan.png)


# Detecting Rogue Machines 
Running a logger for a machine with an SSH port exposed to the public internet, a list is
accumulated for machines that have attempted many times to login. It is amazing how many 
machines are continuously trying to do this, and even more interesting to see where they 
are located. 

![SSH_Attempts](https://raw.githubusercontent.com/scott-robbins/Snoopy/master/OSINT/jerks.png)
