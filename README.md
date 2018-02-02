# ciliatus_controlunit
ciliatus Control Unit for Raspberry PI

# Requirements

* Python 3.6
* [Ciliatus](https://github.com/matthenning/ciliatus) Installation (>=v1.6-beta)
* [RPi.GPIO](https://pypi.python.org/pypi/RPi.GPIO)
* [MyPyDHT](https://github.com/freedom27/MyPyDHT)

# Setup

Generate config in Ciliatus and copy to `config.ini`

# Run

If you're using multiple versions of python:

`sudo python3.6 app.py`

Otherwise

`sudo python app.py`

You can run it in background using nohup:

`sudo nohup python app.py &`

# Supported sensors

MyPyDHT supports the following sensors:

* DHT11
* DHT22
* AM2302
* BME280

Other I2C sensors than BME280 should be relatively simple to implement using the existing infrastructure.
