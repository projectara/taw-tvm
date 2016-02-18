#!/bin/bash

if [ $# -lt 2 ]; then
   echo "Require a Trusted Administrative Procedure as the first argument and a device as the second argument."
   exit 1
fi

cd taps/$1 &&
mkdir -p input_disk.img &&
cp -R input_disk/* input_disk.img &&
cd input_disk.img &&
../fetch_inputs.sh &&
cd .. &&
xorriso -as mkisofs -V "TVM_INPUT" -o input_disk.iso input_disk.img

if [ $# -eq 3 ] && [ $3 = '-usb' ] && [ -w $2 ]; then
    cp input_disk.iso "$2" &&
    echo "Wrote TVM input-disk ISO to USB medium [OK]"
else
    xorriso -as cdrecord dev=$2 -blank=as_needed -eject \
        input_disk.iso &&
    echo "Wrote TVM input-disk ISO image to DVD medium [OK]"
fi
