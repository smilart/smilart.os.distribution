#!/bin/bash

set -vx
#apt-get install debootstrap syslinux squashfs-tools genisoimage memtest86+ rsync gcc


SOURCE=$1 # Path to image-dir
PASSWD=$2
DEVICE=$3
TMP_LOCAL_DIR=/tmp/to_usb

syslinux -i "$DEVICE"1
#dd if=/usr/lib/syslinux/mbr.bin of=$DEVICE conv=notrunc bs=440 count=1
dd if=/usr/sahre/syslinux/mbr.bin of=$DEVICE conv=notrunc bs=440 count=1
[[ ! -d /mnt/usb ]] && mkdir -pv /mnt/usb
mount  "$DEVICE"1 /mnt/usb



[[ -d $TMP_LOCAL_DIR ]] && rm -rv $TMP_LOCACL_DIR
mkdir -pv $TMP_LOCAL_DIR
#rsync -rv root@192.168.1.52:/home/smilart.os.distribution/scripts/installer-build/live_boot/image /tmp/111
#sshpass -p "smilart" rsync -rv root@192.168.1.52:/home/smilart.os.distribution/scripts/installer-build/live_boot/image /tmp/111
sshpass -p $PASSWD rsync -rv  $SOURCE $TMP_LOCAL_DIR

cp $TMP_LOCAL_DIR/image/isolinux/menu.c32 /mnt/usb/ && 
cp $TMP_LOCAL_DIR/image/isolinux/hdt.c32 /mnt/usb/ && 
cp $TMP_LOCAL_DIR/image/live/memtest /mnt/usb/memtest && 
cp $TMP_LOCAL_DIR/image/isolinux/isolinux.cfg /mnt/usb/syslinux.cfg && 
rsync -rv $TMP_LOCAL_DIR/image/live /mnt/usb/

umount /mnt/usb
