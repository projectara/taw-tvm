#!/bin/bash

tar -jxvf gcc-arm-none-eabi-4_8-2014q3-20140805-linux.tar.bz2 &&
echo "export PATH=\"$HOME/gcc-arm-none-eabi-4_8-2014q3/bin:\$PATH\"" >> ~/.profile &&
echo "export PATH=\"$HOME/manifesto:\$PATH:\"" >> ~/.profile &&

source .profile &&

cd flashrom &&
make &&
sudo make install &&
cd .. &&

export PATH=~/bootrom-tools/scripts:~/bootrom-tools:$PATH &&
export BOOTROM_ROOT=~/bootrom &&
export KEY_DIR=~/bin &&
export DROP_ASSEMBLY_DIR=~/bootrom-tools/es3-test &&
export TEST_DROP_DIR=~/es3-test &&
export DELIVERY_NAME=es3-bootrom-delivery &&
export DELIVERY_ROOT=~ &&

cd bootrom-tools/scripts &&
./makedelivery --rev=1b3b7678eea6f8fa8d747f22b31ff119a2396e12 &&

cd ~ &&
mkdir delivery_archive &&
mv *.es3-bootrom-delivery.{tar.gz,sha256} delivery_archive &&
genisoimage -iso-level 4 -o delivery_archive.iso delivery_archive
