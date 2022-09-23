#!/bin/bash

mkfifo /run/exabgp.in; chmod 600 /run/exabgp.in;
mkfifo /run/exabgp.out; chmod 600 /run/exabgp.out;

# Create env file
if [ ! -f /etc/exabgp/exabgp.env ]; then
  exabgp --fi > /etc/exabgp/exabgp.env
  # bind to all interfaces
  sed -i "s/^bind = .*/bind = '0.0.0.0'/" /etc/exabgp/exabgp.env 
  # run as root (otherwise ip add commands wont work)
  sed -i "s/^user = 'nobody'/user = 'root'/" /etc/exabgp/exabgp.env
fi

exabgp /etc/exabgp/exabgp.conf