#!/bin/bash

# Activate SSH by enabling the service
sudo systemctl enable ssh
sudo systemctl start ssh

# Optionally, you can also open the SSH port (22) in the firewall
sudo ufw allow ssh