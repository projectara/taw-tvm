#!/bin/bash

if [ $# -ne 1 ]; then
   echo "Require a USB device as the first argument."
   exit 1
fi

apt-get update &&
apt-get install --assume-yes live-build live-boot live-config &&
echo "Installed Debian Live infrastructure [OK]" &&
mkdir -p taw/image &&
cd taw/image &&
lb config --binary-images iso-hybrid -a i386 &&
echo "Initialized fresh Debian Live template for TAW [OK]" &&
cd config &&
echo "qemu qemu-utils qemu-system python3-dialog xorriso" > package-lists/taw.list.chroot &&
echo "cups cups-client foomatic-db" > package-lists/printing.list.chroot &&
echo "task-cinnamon-desktop" > package-lists/desktop.list.chroot &&
mkdir -p packages.chroot/ &&
cp ../../custom_packages/* packages.chroot/ &&
mkdir -p includes.chroot/ &&
cd includes.chroot/ &&
cp -R ../../../contents/* . &&
mkdir -p etc/skel/tashare &&
cd ../../ &&
lb build &&
echo "Built Debian Live ISO for TAW [OK]" &&
cp live-image-i386.hybrid.iso "$1" &&
echo "Wrote Debian Live ISO to USB medium [OK]"
