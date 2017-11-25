#!/usr/bin/env bash

sudo mount -o remount,rw /
sudo git --work-tree=/home/pi/dotop/ --git-dir=/home/pi/dotop/.git fetch --all 
sudo git --work-tree=/home/pi/dotop/ --git-dir=/home/pi/dotop/.git reset --hard
sudo git --work-tree=/home/pi/dotop/ --git-dir=/home/pi/dotop/.git pull

sudo chown pi:pi /var/log/dotop
sudo chown pi:pi -R /home/pi/dotop/
sudo chmod 770 -R /home/pi/dotop/


sudo telinit 1
sudo mount -o remount,ro /
(sleep 5 && sudo reboot) &
