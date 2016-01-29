#!/bin/sh
sudo dpkg -i --force-all proprietary_printer_drivers/hll2320dcupswrapper_3.2.0-1_i386.deb &&
sudo dpkg -i --force-all proprietary_printer_drivers/hll2320dlpr_3.2.0-1_i386.deb &&
lpadmin -p HL-L2320D-series -o PageSize=Letter &&
lpadmin -d HL-L2320D-series &&
sudo cp /usr/lib/cups/filter/brlpdwrapperHLL2320D /usr/lib64/cups/filter
