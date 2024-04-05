# Copyright (C) 2017 Aleksey Rogov <alex@arogov.com>. All rights reserved.

import machine
import network
from binascii import hexlify, a2b_base64
from bme280 import BME280
from hashlib import sha1
from json import loads
from os import remove
from time import ticks_us
from urllib.urequest import urlopen
from zlib import decompress

SLEEP_TIME = 612000
WD_TIMER = 15000

WIFI_SSID = 'WIFI-AP'
WIFI_BSSID = b'\xAA\xBB\xCC\xDD\xEE\xFF'
WIFI_KEY = 'password'

IFCONFIG_IP = '192.168.1.254'
IFCONFIG_MASK = '255.255.255.0'
IFCONFIG_GW = '192.168.1.1'
IFCONFIG_DNS = '192.168.1.1'

BREAK_PIN = 13
SCL_PIN = 4
SDA_PIN = 5

SERVER_KEY = '1234567890qwertyuiop_asdfghjklzxcvbnm-ASDFGHJKLZ'
SERVER_URL = 'https://example.com/thermo'

MAIN_FILE_NAME = 'main.py'


def deepsleep(period):
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, period)
    machine.deepsleep()


def wd_handler(calledvalue):
    print(f'[{ticks_us() / 1000000:12.6f}] Diconnecting from network')
    wlan.disconnect()
    print(f'[{ticks_us() / 1000000:12.6f}] Pulling down interface')
    wlan.active(False)
    print(f'[{ticks_us() / 1000000:12.6f}] Sleeping.')
    deepsleep(SLEEP_TIME)


pin = machine.Pin(BREAK_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

if pin.value() == 1:
    print(f'[{ticks_us() / 1000000:12.6f}] Copyright (C) 2017 Aleksey Rogov <alex@arogov.com>. All rights reserved.')

    print(f'[{ticks_us() / 1000000:12.6f}] Init watchdog timer...', end='')
    wd_scheduler = machine.Timer(-1)
    wd_scheduler.init(period=WD_TIMER, mode=machine.Timer.PERIODIC, callback=wd_handler)

    print(f'OK\n[{ticks_us() / 1000000:12.6f}] Connecting to network...', end='')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.ifconfig((IFCONFIG_IP, IFCONFIG_MASK, IFCONFIG_GW, IFCONFIG_DNS))
    if wlan.config('essid') == WIFI_SSID:
        wlan.connect()
    else:
        wlan.connect(WIFI_SSID, WIFI_KEY, bssid=WIFI_BSSID)

    print(f'OK\n[{ticks_us() / 1000000:12.6f}] Calculating SHA1: ', end='')
    s = sha1()
    with open(MAIN_FILE_NAME, 'rb') as f:
        for line in f:
            s.update(line)
    sha1 = hexlify(s.digest()).decode('utf-8')
    print(sha1)

    print(f'[{ticks_us() / 1000000:12.6f}] Gathering data from sensor: ', end='')
    try:
        i2c = machine.I2C(scl=machine.Pin(SCL_PIN), sda=machine.Pin(SDA_PIN))
        bme = BME280(i2c=i2c)
        cd = bme.read_compensated_data()
    except:
        cd = [0, 0, 0]
        print('Fail')
    else:
        print(f't = {cd[0] / 100:.1f} C; P = {cd[1] / 256:.3f} Pa; RH = {cd[2] / 1024:.1f}%')

    adcv = machine.ADC(0).read()
    print(f'[{ticks_us() / 1000000:12.6f}] ADC value = {adcv}')

    mac = hexlify(network.WLAN().config('mac')).decode('utf-8')
    uniq_id = hexlify(machine.unique_id()).decode('utf-8')

    while not wlan.isconnected():
        machine.idle()
    print(f'[{ticks_us() / 1000000:12.6f}] Connected')
    print(f'[{ticks_us() / 1000000:12.6f}] Sending data to server...', end='')
    s = urlopen(SERVER_URL, data=f'key={SERVER_KEY}&sid={uniq_id}&mac={mac}&temp={cd[0] / 100}&pres={cd[1] / 256}&hum={cd[2] / 1024}&adc={adcv}&sha1={sha1}')
    print(f'OK\n[{ticks_us() / 1000000:12.6f}] Reading response: ', end='')

    tmp = s.readline()
    try:
        status = loads(tmp)
    except ValueError:
        print(f'FAIL.\n[{ticks_us() / 1000000:12.6f}] Incorrect server response. Sleeping')
        deepsleep(SLEEP_TIME)

    print(f'status: {status["status"]}, reason: {status["reason"]}')
    recvd_sha1 = status.get('sha1')
    if recvd_sha1 and recvd_sha1 != sha1:
        print(f'New firmware is available with SHA1 {status["sha1"]}\nDownloading...', end='')
        base64_data = s.read()
        s.close()
        print('OK')
        zip_data = a2b_base64(base64_data)
        del(base64_data)
        gc.collect()
        fw_new = decompress(zip_data)
        del(zip_data)
        gc.collect()
        new_fw_sha1 = hexlify(sha1(fw_new).digest()).decode('utf-8')
        if recvd_sha1 == new_fw_sha1:
            remove(MAIN_FILE_NAME)
            f = open(MAIN_FILE_NAME, 'wb+')
            f.write(fw_new)
            f.close()
            print(f'Firmware successfully upgraded with SHA1 {new_fw_sha1}')
        else:
            print(f'SHA1 error: {recvd_sha1} vs {new_fw_sha1}')
    else:
        s.close()
    wd_handler(None)
else:
    print(f'[{ticks_us() / 1000000:12.6f}] Break pin is pulled down.')
