# ciliatus_controlunit
Ciliatus Control Unit
Primarily used for GPIO controlled sensors on a Raspberry Pi

# Requirements

* Python >=3.6
* [Ciliatus](https://github.com/matthenning/ciliatus) >=v2.0
* [RPi.GPIO](https://pypi.python.org/pypi/RPi.GPIO) (for Raspberry PIs)
* [MyPyDHT](https://github.com/freedom27/MyPyDHT) (for Raspberry PIs)

# Setup

* Generate config in Ciliatus and copy to `config.ini`.
* Add authentication tokens

# Run

If you're using multiple versions of python:

`sudo python3.6 app.py`

Otherwise

`sudo python app.py`

You can run it in background using nohup:

`sudo nohup python app.py &`

Note: root permissions are only required for GPIO access.

# Supported sensors

MyPyDHT supports the following sensors:

* DHT11
* DHT22
* AM2302
* BME280

Other sensors should be relatively simple to implement using the existing infrastructure.

# Troubleshooting

### I2C devices are not responding or not showing up

I2C is sensitive to high distances. Try lowering the I2C clock and using a shielded cable.
Lowering the clock on RaspberryPi is done by adding the following line in /boot/config.txt:
`dtparam=i2c_arm_baudrate=frequency`

Replace *frequency* with your desired clock. 20kHz is reommended for up to 30m.
