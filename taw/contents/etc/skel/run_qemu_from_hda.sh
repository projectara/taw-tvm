#!/bin/sh
qemu-system-i386 -m 2048 -hda $1 -virtfs local,path=tashare,mount_tag=tashare,security_model=passthrough,id=host1
