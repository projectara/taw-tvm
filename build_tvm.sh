#!/bin/bash

if [ $# -ne 2 ]; then
   echo "Require a Trusted Administrative Procedure as the first argument and a USB device as the first argument."
   exit 1
fi

if [ -f taps/$1/arch ]; then
   export ARCH=$(cat taps/$1/arch)
   echo "Architecture requirement detected: $ARCH"
else
   export ARCH=amd64
fi

apt-get update &&
apt-get install --assume-yes live-build live-boot live-config &&
cd taps/$1 &&
mkdir -p tvm &&
cd tvm &&
lb config --binary-images iso-hybrid -a $ARCH &&
echo "Initialized fresh Debian Live template for TVM [OK]" &&
cat ../packages > config/package-lists/tvm.list.chroot &&
echo "Added package list for Trusted VM to image template [OK]" &&
cd config/includes.chroot/ &&
mkdir -p etc/skel &&
cd etc/skel &&
../../../../../fetch.sh &&
cp -R ../../../../../contents/* . &&
echo "Downloaded needed repositories and archives into live-user home directory for TVM [OK]" &&
cd ../../../../ &&
sudo lb build &&
cp live-image-$ARCH.hybrid.iso "$2" &&
echo "Wrote Debian Live ISO to USB medium [OK]"
