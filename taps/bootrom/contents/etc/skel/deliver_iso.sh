#!/bin/bash

genisoimage -iso-level 4 -o delivery_archive.iso delivery_archive &&
mv delivery_archive.iso ROMCodeDeliveryNotice.pdf /media/user/tashare/