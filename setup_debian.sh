#!/bin/bash
echo "Installing dependencies ..."
sudo apt-get install build-essential python-dev python-setuptools git

echo "Installiong RPi.GPIO ..."
sudo apt-get install python{,3}-rpi.gpio

echo "Installing MyPyDHT ..."
git clone --recursive https://github.com/freedom27/MyPyDHT
cd MyPyDHT/
sudo python setup.py install
cd ..

echo "Installing ciliatus controlunit ..."
sudo python setup.py