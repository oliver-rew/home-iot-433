#!/usr/bin/python3

# Import Python System Libraries
import time
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board

# Import the RFM69 radio module.
import adafruit_rfm69

from bitarray import bitarray
import blynklib
import os

# initialize Blynk
BLYNK_AUTH = os.getenv('BLYNK_AUTH')
if BLYNK_AUTH == "":
    print("BLYNK_AUTH not set")
    os.exit(1)

blynk = blynklib.Blynk(BLYNK_AUTH)

# attach device 1 to pin V1
@blynk.handle_event('write V1')
def write_virtual_pin_handler(pin, value):
    pin_val = value[0]
    if pin_val == "1":
        print("Turn on V1")
        on(dev1)
    elif pin_val == "0":
        print("Turn off V1")
        off(dev1)

# attach device 2 to pin V2
@blynk.handle_event('write V2')
def write_virtual_pin_handler(pin, value):
    pin_val = value[0]
    if pin_val == "1":
        print("Turn on V2")
        on(dev2)
    elif pin_val == "0":
        print("Turn off V2")
        off(dev2)

# attach device 3 to pin V3
@blynk.handle_event('write V3')
def write_virtual_pin_handler(pin, value):
    pin_val = value[0]
    if pin_val == "1":
        print("Turn on V3")
        on(dev3)
    elif pin_val == "0":
        print("Turn off V3")
        off(dev3)

# Configure Packet Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, 433.92)
prev_packet = None

rfm69.encryption_key = None # no excryption key
rfm69.modulation_type = 1 # OOK modulation
rfm69.bitrate = 3723    # this matches the outlet signal
rfm69.dc_free = 0 # no manchester encoding
rfm69.modulation_shaping = 0 # no gaussian filter
rfm69.preamble_length = 0 # no preamble
rfm69.sync_word = None # no sync word
rfm69.crc_on = 0 # no crc
rfm69.packet_format = 0 # fixed length packet

# zero all node identification headers
rfm69.destination = 0
rfm69.node = 0
rfm69.identifier = 0
rfm69.flags = 0

# rfm_send defines a simpler send func that the library, and removes 
# some of the encoded information
def rfm_send(rfm, data):
    rfm.idle()
    # Write payload to transmit fifo
    rfm._write_from(adafruit_rfm69._REG_FIFO, data)
    # Turn on transmit mode to send out the packet.
    rfm.transmit()
    # Wait for packet sent interrupt with explicit polling (not ideal but
    # best that can be done right now without interrupts).
    start = time.monotonic()
    timed_out = False
    while not timed_out and not rfm.packet_sent():
        if (time.monotonic() - start) >= rfm.xmit_timeout:
            timed_out = True

    # go back to idle
    rfm69.idle()

# ppm message components

# the original signal had a sync bit followed by approx 5
# zero bit times. The RFM69 seems to always insert a single
# high bit at the beginning of a transmission, so just pad
# 5 bit times at the beginning to make the sync header
sync = bitarray('0000000000')

# ppm binary representations in approx bit times
one = bitarray('100000')
zero = bitarray('10')

# outlet message header and footer
header = ([0x66, 0x56, 0x9a, 0x9a, 0xaa, 0x55])
footer = ([0x00])

# byte that determines on/off
dev_on = ([0x96])
dev_off = ([0x95])

# device bytes
dev1 = ([0xaa])
dev2 = ([0xa9])
dev3 = ([0xa6])
dev4 = ([0xa5])
dev5 = ([0x9a])

def byte_to_ppm_byte(b):
    ppm_byte = bitarray()
    for i in reversed(range(8)):
        if b & 1<<i:
            ppm_byte += one
        else:
            ppm_byte += zero

    return ppm_byte

def on(dev):
    print("turning on...")
    msg = header +  dev_on + dev + footer

    data = bitarray()
    data += sync

    for b in msg:
        data += byte_to_ppm_byte(b)

    rfm_send(rfm69, data.tobytes())

def off(dev):
    print("turning off...")
    msg = header + dev_off + dev + footer

    data = bitarray()
    data += sync

    for b in msg:
        data += byte_to_ppm_byte(b)

    rfm_send(rfm69, data.tobytes())

# run blynk
while True:
    blynk.run()
