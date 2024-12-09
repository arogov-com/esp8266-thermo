# esp8266-thermo
A simple weather station project based on ESP8266, MicroPython and BME280.
It is possible to automatically synchronize the software with the server.

## Install
1. Burn the module with the Micropython image. https://micropython.org/download/esp8266/
```
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash --flash_size=detect 0 esp8266-20220618-v1.19.1.bin
```
2. Put the <i>File: [main_fw.py](https://github.com/arogov-com/esp8266-thermo/blob/master/main_fw.py)</i> to the module's FS.
```
ampy -p /dev/ttyAMA0 -b 115200 put main.py /main.py
```
3. Build the docker image
```
make build
```
4. Run container on the server
```
docker compose up -d
```

## Flowchart
![esp8266-thermo-fc](https://user-images.githubusercontent.com/34504035/225302183-e3161c05-bec9-42e1-a1b9-02200308c54f.png)

## Schematics
![esp8266-thermo](https://user-images.githubusercontent.com/34504035/224777200-c6ba177d-f591-4194-a915-3057da11c480.png)
