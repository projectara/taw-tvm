#!/bin/bash

source bootrom_env.sh &&

tar -jxvf gcc-arm-none-eabi-4_8-2014q3-20140805-linux.tar.bz2 &&
echo "export PATH=\"$HOME/gcc-arm-none-eabi-4_8-2014q3/bin:\$PATH\"" >> ~/.profile &&
echo "export PATH=\"$HOME/manifesto:\$PATH:\"" >> ~/.profile &&

cd flashrom &&
make
