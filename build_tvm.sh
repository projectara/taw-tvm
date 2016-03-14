#!/bin/bash

#  Copyright (c) 2015-2016 Google Inc.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#  1. Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#  3. Neither the name of the copyright holder nor the names of its
#  contributors may be used to endorse or promote products derived from this
#  software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
cd config/ &&
cp -R ../../config/* . &&
cd includes.chroot/ &&
../../../fetch.sh &&
mkdir -p media/user/tashare &&
mkdir -p media/input_cdrom &&
echo "Copied disk contents into TVM image [OK]" &&
cd ../.. &&
sudo lb build &&
xorriso -dev live-image-$ARCH.hybrid.iso -volid "TVM_$1_Debian_live" \
        -boot_image any keep &&

if [ $# -eq 3 ] && [ $3 = '-usb' ] && [ -w $2 ]; then
    cp live-image-$ARCH.hybrid.iso "$2" &&
    echo "Wrote Debian Live ISO to USB medium [OK]"
else
    xorriso -as cdrecord dev=$2 -blank=as_needed -eject \
        live-image-$ARCH-hybrid.iso &&
    echo "Wrote Debian Live ISO image to DVD medium [OK]"
fi
