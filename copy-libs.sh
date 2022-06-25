#!/bin/sh

DEV_DIR="/Users/erin/SynologyDrive/Personal/CurciutPython/adafruit-circuitpython-bundle-7.x-mpy-20220623/lib"
MP_DIR="/Volumes/CIRCUITPY/lib"

LIBS=("adafruit_matrixportal" \
"adafruit_portalbase" \
"adafruit_esp32spi" \
"adafruit_bus_device" \
"adafruit_requests.mpy" \
"adafruit_fakerequests.mpy" \
"adafruit_io" \
"adafruit_bitmap_font" \
"adafruit_display_text" \
#"adafruit_minimqtt" \
#"adafruit_lis3dh.mpy" \
"neopixel.mpy" )

for L in ${LIBS[@]}; do
  echo $L " to " $MP_DIR
  cp -R $DEV_DIR/$L $MP_DIR/.
done