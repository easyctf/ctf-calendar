#!/bin/bash

echo "Updating system..."
apt-get -y update
apt-get -y upgrade

apt-get -y install python-dev python-pip libffi-dev
apt-get -y install postgresql postgresql-contrib libpq-dev

cd /vagrant

pip install -r requirements.txt