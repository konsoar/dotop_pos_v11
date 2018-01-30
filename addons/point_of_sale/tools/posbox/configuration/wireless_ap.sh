#!/usr/bin/env bash

FORCE_HOST_AP="FORCE_HOST_AP"
WIRED_IP=$(ifconfig eth0 | grep "inet " | awk -F: '{print $1}' | awk '{print $2}';)
WIFI_NETWORK_FILE="/home/pi/wifi_network.txt"

# if there is no wired ip, attempt to start an AP through wireless interface
logger -t posbox_wireless_ap "No wired IP"

ifconfig wlan0 down
ifconfig wlan0 up

# wait for wlan0 to come up
sleep 5

# we cannot scan for networks while in Master mode
# so first scan and save the networks to a list
iwlist wlan0 scan | grep 'ESSID:' | sed 's/.*ESSID:"\(.*\)"/\1/' | sort -u > /tmp/scanned_networks.txt

# only do it when there is a wireless interface
if [ -n "$(iw list)" ] ; then
    if [ -f "${WIFI_NETWORK_FILE}" ] && [ -z "${FORCE_HOST_AP}" ] ; then
        logger -t posbox_wireless_ap "Loading persistently saved setting"
        /home/pi/dotop/addons/point_of_sale/tools/posbox/configuration/connect_to_wifi.sh &
    else
        logger -t posbox_wireless_ap "Starting AP"

        service hostapd restart

        ip addr add 10.11.12.1/24 dev wlan0

        service isc-dhcp-server restart

        service dotop restart
    fi
# no wired, no wireless
else
    service dotop restart
fi
