#!/bin/bash

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
