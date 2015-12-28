#!/bin/sh
qemu-img create -f qcow2 $2_hda.qcow2 32G &&
qemu-system-i386 -m 2048 -cdrom $1 -hda $2_hda.qcow2 -virtfs local,path=tashare,mount_tag=tashare,security_model=passthrough,id=host1
