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
cat ../../packages > package-lists/taw.list.chroot &&
echo "task-cinnamon-desktop" > package-lists/desktop.list.chroot &&
mkdir -p includes.chroot/ &&
cd includes.chroot/ &&
cp -R ../../../contents/* . &&
mkdir -p etc/skel/tashare &&
cd ../../ &&
lb build &&
xorriso -dev live-image-amd64.hybrid.iso -volid "TAW_Debian_live" &&
echo "Built Debian Live ISO for TAW [OK]" &&

if [ $# -eq 2 ] && [ $2 = '-usb' ] && [ -w $1 ]; then
    cp live-image-amd64.hybrid.iso "$1" &&
    echo "Wrote Debian Live ISO to USB medium [OK]"
else
    xorriso -as cdrecord dev=$1 -blank=as_needed -eject \
        live-image-amd64-hybrid.iso &&
    echo "Wrote Debian Live ISO image to DVD medium [OK]"
fi
