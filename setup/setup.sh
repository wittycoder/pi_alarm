#!/bin/sh

# install pip for python
apt-get -y install python-setuptools
easy_install pip

# install sqlite3 database
apt-get -y install sqlite3

# install flask, for webservice
pip install --upgrade flask

# install and setup haproxy for port 80 forwarding
apt-get -y install haproxy
mv /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.bak
cp haproxy.cfg /etc/haproxy
cp haproxy /etc/default
service haproxy start

# Install players for sound generator and MP3s
apt-get -y install sox
apt-get -y install mpg123

# mkdir for the install
mkdir /opt/pi_alarm/

# copy all of the files required to run the app
pwd
cp -R ../* /opt/pi_alarm

# Setup the init files
cp pi_alarm pi_alarm_daemon /etc/init.d
update-rc.d pi_alarm defaults
update-rc.d pi_alarm_daemon defaults

/etc/init.d/pi_alarm start
/etc/init.d/pi_alarm_daemon start
