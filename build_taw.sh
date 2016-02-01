#!/bin/bash

if [ $# -lt 1 ]; then
   echo "Require a writable device as the first argument."
   exit 1
fi

apt-get update &&
apt-get install --assume-yes live-build live-boot live-config xorriso &&
echo "Installed Debian Live infrastructure [OK]" &&
mkdir -p taw/image &&
cd taw/image &&
lb config --binary-images iso-hybrid -a amd64 &&
echo "Initialized fresh Debian Live template for TAW [OK]" &&
cd config &&
echo "qemu qemu-utils qemu-system python3-dialog xorriso" > package-lists/taw.list.chroot &&
echo "task-cinnamon-desktop" > package-lists/desktop.list.chroot &&
mkdir -p includes.chroot/ &&
cd includes.chroot/ &&
cp -R ../../../contents/* . &&
mkdir -p etc/skel/tashare &&
cd ../../ &&
lb build &&
echo "Built Debian Live ISO for TAW [OK]" &&

if [ $# -eq 2 ] && [ $2 = '-usb' ] && [ -w $1 ]; then
    cp live-image-amd64.hybrid.iso "$1" &&
    echo "Wrote Debian Live ISO to USB medium [OK]"
else
    xorriso -as cdrecord dev=$1 -blank=as_needed -eject \
        live-image-amd64-hybrid.iso &&
    echo "Wrote Debian Live ISO image to DVD medium [OK]"
fi
