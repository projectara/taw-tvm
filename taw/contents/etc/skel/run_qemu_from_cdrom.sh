#!/bin/sh
qemu-system-i386 -m 2048 -cdrom $1 -enable-kvm -cpu host -virtfs local,path=tashare,mount_tag=tashare,security_model=passthrough,id=host1
