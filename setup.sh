#!/bin/bash

MYSQL_ROOT_PASSWORD=`cat /vagrant/MYSQL_ROOT_PASSWORD`

echo "Updating system..."
sudo apt-get -y update
sudo apt-get -y upgrade

echo "Preparing for MySQL installation..."
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password password $MYSQL_ROOT_PASSWORD"
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $MYSQL_ROOT_PASSWORD"

echo "Installing dependencies..."
sudo apt-get install -y libffi=3.1~rc1+r3.0.13-12ubuntu0.1
sudo apt-get install -y mysql-server

echo "Installing pip dependencies..."
sudo pip3 install -r /vagrant/requirements.txt

echo "PATH=$PATH:/vagrant" >> /etc/profile
source /etc/profile

sudo sed -i s/127.0.0.1/0.0.0.0/ /etc/mysql/my.cnf
sudo service mysql restart
mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<EOF
CREATE DATABASE easyctf_cal;
EOF
