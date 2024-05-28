#!/bin/bash

SSID=scoreboard
PASS=scoreboard
# Set WIFI Country
raspi-config nonint do_wifi_country US

# Update
apt-get update;
apt-get --assume-yes upgrade;

#Install python
apt-get --assume-yes install python3-pip
pip3 install RPi.GPIO flask

#Hotspot
apt-get --assume-yes install hostapd dnsmasq
systemctl unmask hostapd
systemctl enable hostapd

#CONFIG
echo -e "\ninterface wlan0\n    static ip_address=10.1.1.1/24\n    nohook wpa_supplicant\n" >> /etc/dhcpcd.conf
echo -e "interface=wlan0\ndhcp-range=10.1.1.200,10.1.1.225,255.255.255.0,24h\ndhcp-option=3\ndhcp-option=6\n" > /etc/dnsmasq.conf
echo -e "country_code=US\ninterface=wlan0\nssid=$SSID\nhw_mode=g\nchannel=6\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=2\nwpa_passphrase=$PASS\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP" > /etc/hostapd/hostapd.conf