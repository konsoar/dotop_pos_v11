#!/usr/bin/env bash

# call with ESSID and optionally a password
# when called without an ESSID, it will attempt
# to reconnect to a previously chosen network
function connect () {
	WPA_PASS_FILE="/tmp/wpa_pass.txt"
	PERSISTENT_WIFI_NETWORK_FILE="/home/pi/wifi_network.txt"
	CURRENT_WIFI_NETWORK_FILE="/tmp/current_wifi_network.txt" # used to repair connection when we lose it
	LOST_WIFI_FILE="/tmp/lost_wifi.txt"
	ESSID="${1}"
	PASSWORD="${2}"
	PERSIST="${3}"
	NO_AP="${4}"

	sleep 3

	sudo pkill -f keep_wifi_alive.sh
	WIFI_WAS_LOST=$?

	# make network choice persistent
	if [ -n "${ESSID}" ] ; then
		if [ -n "${PERSIST}" ] ; then
			logger -t posbox_connect_to_wifi "Making network selection permanent"
			sudo mount -o remount,rw /
			echo "${ESSID}" > ${PERSISTENT_WIFI_NETWORK_FILE}
			echo "${PASSWORD}" >> ${PERSISTENT_WIFI_NETWORK_FILE}
			sudo mount -o remount,ro /
		fi
	else
		logger -t posbox_connect_to_wifi "Reading configuration from ${PERSISTENT_WIFI_NETWORK_FILE}"
		ESSID=$(head -n 1 "${PERSISTENT_WIFI_NETWORK_FILE}" | tr -d '\n')
		PASSWORD=$(tail -n 1 "${PERSISTENT_WIFI_NETWORK_FILE}" | tr -d '\n')
	fi

	echo "${ESSID}" > ${CURRENT_WIFI_NETWORK_FILE}
	echo "${PASSWORD}" >> ${CURRENT_WIFI_NETWORK_FILE}

	logger -t posbox_connect_to_wifi "Connecting to ${ESSID}"
	sudo service hostapd stop
	sudo service isc-dhcp-server stop
	logger -t posbox_connect_to_wifi "Connecting to XXXX ---10099"

	sudo pkill wpa_supplicant
	sudo ifconfig wlan0 down
	#sudo iwconfig wlan0 mode ad-hoc
	sudo ifconfig wlan0 0.0.0.0  # this is how you clear the interface's configuration
	sudo ifconfig wlan0 up
	logger -t posbox_connect_to_wifi "Connecting to XXXX ---10000"
	if [ -z "${PASSWORD}" ] ; then
		sudo iwconfig wlan0 essid "${ESSID}"
		logger -t posbox_connect_to_wifi "Connecting to XXXX ---10001"
	else
		sudo wpa_passphrase "${ESSID}" "${PASSWORD}" > "${WPA_PASS_FILE}"
		sudo wpa_supplicant -B -i wlan0 -c "${WPA_PASS_FILE}"
		logger -t posbox_connect_to_wifi "Connecting to XXXX ---10002"
	fi
	logger -t posbox_connect_to_wifi "Connecting to XXXX ---ACCOUNT: ${ESSID} ${PASSWORD} "
	sudo service dhcpcd restart
	logger -t posbox_connect_to_wifi "Connecting to test ifconfig ${ ifconfig wlan0}"
	# give dhcp some time
	timeout 30 sh -c 'until ifconfig wlan0 | grep "inet" ; do sleep 0.1 ; done'
	TIMEOUT_RETURN=$?
	logger -t posbox_connect_to_wifi "Connecting to XXXX ${TIMEOUT_RETURN}"
	if [ ${TIMEOUT_RETURN} -eq 124 ] && [ -z "${NO_AP}" ] ; then
		logger -t posbox_connect_to_wifi "Failed to connect, forcing Posbox AP"
		sudo /home/pi/dotop/addons/point_of_sale/tools/posbox/configuration/wireless_ap.sh "force" &
	else
		if [ ${TIMEOUT_RETURN} -ne 124 ] ; then
			rm -f "${LOST_WIFI_FILE}"
		fi

		if [ ! -f "${LOST_WIFI_FILE}" ] ; then
			logger -t posbox_connect_to_wifi "Restarting dotop"
			sudo service dotop restart
		fi

		if [ ${WIFI_WAS_LOST} -eq 0 ] ; then
			touch "${LOST_WIFI_FILE}"
		fi
		logger -t posbox_connect_to_wifi "Starting wifi keep alive script"
		/home/pi/dotop/addons/point_of_sale/tools/posbox/configuration/keep_wifi_alive.sh &
	fi
}

connect "${1}" "${2}" "${3}" "${4}" &
