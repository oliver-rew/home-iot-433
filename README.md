# home-iot-433

Simple shim application to connect the Blynk API to an adafruit RFM69 radio
bonnet. I use it to control radio controlled outlets via Blynk. 

I use these outlets:
https://www.amazon.com/gp/product/B089N94FRT/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&th=1

Blynk:
https://blynk.io/

## Disclaimer
First of all, I had to tailor the 433MHz control payload for my exact 
outlets, so mileage may vary with other outlets. It is not terribly 
hard to reverse engineer the protocol. I used an RTL-SDR and the 
awesome `rtl_433` tool to figure out the protocol.

## Installation
- enable SPI with `sudo raspi-config` and reboot
- Install the adafruit circuit python libraries here:
https://learn.adafruit.com/adafruit-radio-bonnets/rfm69-raspberry-pi-setup
- Install Blynk and misc packages:
```
$ sudo pip3 install bitarray blynklib
```
- Download Blynk app, create an prject, and connect toogle switchs to pins V1-V3(more
  possible, of course)
- Get the Blynk auth token and put it in `home-iot-433.service`
- Install the service file and start service
```
$ sudo cp home-iot-433.service /etc/systemd/system/
$ sudo systemctl enable home-iot-433.service
$ sudo systemctl restart home-iot-433.service
$ sudo systemctl status home-iot-433.service
```
- Enjoy!

