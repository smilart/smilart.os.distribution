#!/bin/bash

set -vx
#apt-get install debootstrap syslinux squashfs-tools genisoimage memtest86+ rsync gcc


SOURCE=$1 # Path to image-dir
DEVICE=$2
TMP_LOCAL_DIR=/tmp/to_usb/image

syslinux -i /dev/$DEVICE
# ? of=/dev/sdf ?
# dd if=/usr/lib/syslinux/mbr.bin of=/dev/sdf conv=notrunc bs=440 count=1
dd if=/usr/lib/syslinux/mbr.bin of=/dev/$DEVICE conv=notrunc bs=440 count=1
mount /dev/$DEVICE /mnt/usb

[[ -d $TMP_LOCAL_DIR ]] && rm -rv $TMP_LOACL_DIR
mkdir -pv $TMP_LOCAL_DIR
rsync $TMP_LOCAL_DIR $SOURCE

cp $TMP_LOCAL_DIR/isolinux/menu.c32 /mnt/usb/ && 
cp $TMP_LOCAL_DIR/isolinux/hdt.c32 /mnt/usb/ && 
cp $TMP_LOCAL_DIR/live/memtest /mnt/usb/memtest && 
cp $TMP_LOCAL_DIR/isolinux/isolinux.cfg /mnt/usb/syslinux.cfg && 
rsync -rv $TMP_LOCAL_DIR/live /mnt/usb/

