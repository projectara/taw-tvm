#!/bin/bash

if [ $# -lt 2 ]; then
   echo "Require a Trusted Administrative Procedure as the first argument and a device as the second argument."
   exit 1
fi

if [ -f taps/$1/arch ]; then
   export ARCH=$(cat taps/$1/arch)
   echo "Architecture requirement detected: $ARCH"
else
   export ARCH=amd64
fi

apt-get update &&
apt-get install --assume-yes live-build live-boot live-config xorriso &&
cd taps/$1 &&
mkdir -p tvm &&
cd tvm &&
lb config --binary-images iso-hybrid -a $ARCH --debian-installer live &&
echo "Initialized fresh Debian Live template for TVM [OK]" &&
# Add cross-TAP packages to the specific TVM's package list
cat ../../packages > config/package-lists/tvm.list.chroot &&
cat ../packages >> config/package-lists/tvm.list.chroot &&
echo "Added package list for Trusted VM to image template [OK]" &&
cd config/includes.chroot/ &&
cp -R ../../../contents/* . &&
../../../fetch.sh &&
mkdir -p media/user/tashare &&
mkdir -p media/input_cdrom &&
echo "Copied disk contents into TVM image [OK]" &&
cd ../.. &&
sudo lb build &&
xorriso -dev live-image-amd64.hybrid.iso -volid "TVM_$1_Debian_live" &&

if [ $# -eq 3 ] && [ $3 = '-usb' ] && [ -w $2 ]; then
    cp live-image-$ARCH.hybrid.iso "$2" &&
    echo "Wrote Debian Live ISO to USB medium [OK]"
else
    xorriso -as cdrecord dev=$2 -blank=as_needed -eject \
        live-image-$ARCH-hybrid.iso &&
    echo "Wrote Debian Live ISO image to DVD medium [OK]"
fi
