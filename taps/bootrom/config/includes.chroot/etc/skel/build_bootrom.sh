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

source bootrom_env.sh

cd bootrom-tools/scripts &&
./makedelivery --rev=1b3b7678eea6f8fa8d747f22b31ff119a2396e12 &&

cd ~/Toshiba_Drop &&
tar -zxvf 20151016-2042-PDT.es3-bootrom-delivery.tar.gz &&
sha256sum < es3-bootrom-delivery/bromcAP.bin > es3-bootrom-delivery/bromcAP.sha256 &&
sha256sum < es3-bootrom-delivery/bromcGP.bin > es3-bootrom-delivery/bromcGP.sha256 &&
cd .. &&
./compare_bootroms.py Toshiba_Drop/es3-bootrom-delivery/bromcAP.dat es3-bootrom-delivery/bromcAP.dat &&
./compare_bootroms.py Toshiba_Drop/es3-bootrom-delivery/bromcGP.dat es3-bootrom-delivery/bromcGP.dat &&
./report.py ROMCodeDeliveryNotice.html.template 1b3b7678eea6f8fa8d747f22b31ff119a2396e12 > ROMCodeDeliveryNotice.html &&
xvfb-run --server-args="-screen 0, 1024x768x24" /usr/bin/wkhtmltopdf ROMCodeDeliveryNotice.html ROMCodeDeliveryNotice.pdf &&

cd ~ &&
mkdir delivery_archive &&
mv *.es3-bootrom-delivery.{tar.gz,sha256} delivery_archive &&
cp ROMCodeDeliveryNotice.pdf delivery_archive
