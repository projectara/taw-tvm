#!/bin/bash

if [ $# -ne 1 ]; then
   echo "Require a USB device as the first argument."
   exit 1
fi

apt-get update &&
apt-get install --assume-yes live-build live-boot live-config &&
echo "Installed Debian Live infrastructure [OK]" &&
mkdir -p taw/image &&
cd taw/image &&
lb config --binary-images iso-hybrid &&
echo "Initialized fresh Debian Live template for TAW [OK]" &&
cd config &&
echo "qemu qemu-utils qemu-system" > package-lists/twa.list.chroot &&
echo "task-cinnamon-desktop" > package-lists/desktop.list.chroot &&
mkdir -p includes.chroot/etc/skel &&
echo -en "#!/bin/sh\nqemu-img create -f qcow2 \$2_hda.qcow2 32G &&\nqemu-system-i386 -m 2048 -cdrom \$1 -hda \$2_hda.qcow2\n" > includes.chroot/etc/skel/install_tvm.sh &&
echo -en "#!/bin/sh\nqemu-system-i386 -m 2048 -cdrom \$1\n" > includes.chroot/etc/skel/run_qemu.sh &&
chmod +x includes.chroot/etc/skel/{install_tvm,run_qemu}.sh &&
cd .. &&
lb build &&
echo "Built Debian Live ISO for TAW [OK]" &&
cp live-image-amd64.hybrid.iso "$1" &&
echo "Wrote Debian Live ISO to USB medium [OK]"
