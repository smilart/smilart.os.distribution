#!/bin/bash

set -vx
#apt-get install debootstrap syslinux squashfs-tools genisoimage memtest86+ rsync gcc
if [ -z "$1" ]; then
    ARCH="amd64"
else
    ARCH=$1
fi

if [ -z "$2" ]; then
    BUILD_DIR="live_boot"
else
    BUILD_DIR=$2
fi

[[ -d $BUILD_DIR ]] && rm -rfv $BUILD_DIR
mkdir $BUILD_DIR && cd $BUILD_DIR

debootstrap --arch=$ARCH --variant=minbase wheezy chroot http://ftp.us.debian.org/debian/
mount -o bind /dev chroot/dev &&  cp /etc/resolv.conf chroot/etc/resolv.conf

cp -pv ../in_chroot.sh  chroot/tmp/
cp -pv ../to_iso/autologin.c chroot/tmp
cp -pv ../to_iso/inittab chroot/etc/inittab
gcc ../to_iso/autologin.c -o chroot/usr/local/sbin/autologin
mkdir -p chroot/var/lib/smilart_srv/scripts && cp -pv ../../smilartos-install/smilartos-install.py chroot/var/lib/smilart_srv/scripts/smilartos-install.py && cp -pv ../to_iso/config_network.sh chroot/var/lib/smilart_srv/scripts/config_network.sh
cp -pv ../to_iso/smilartos-install chroot/etc/init.d/smilartos-install

wget https://pypi.python.org/packages/source/u/urwid/urwid-1.2.1.tar.gz -P chroot/tmp

chroot chroot /bin/bash -c "/tmp/in_chroot.sh $ARCH" 

cp -pv ../to_iso/default.nginx chroot/etc/nginx/sites-available/default

umount -lf chroot/dev
mkdir -p image/{live,isolinux}
mksquashfs chroot image/live/filesystem.squashfs #-e boot

cp chroot/boot/vmlinuz-3.2.0-4-$ARCH image/live/vmlinuz1 && 
cp chroot/boot/initrd.img-3.2.0-4-$ARCH image/live/initrd1

cp ../to_iso/isolinux.cfg image/isolinux/isolinux.cfg

cp /usr/lib/syslinux/isolinux.bin image/isolinux/ && 
cp /usr/lib/syslinux/menu.c32 image/isolinux/ && 
cp /usr/lib/syslinux/hdt.c32 image/isolinux/ && 
cp /boot/memtest86+.bin image/live/memtest

cd image && 
genisoimage -rational-rock -volid "Debian Live" -cache-inodes -joliet -full-iso9660-filenames -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -output ../debian-live-$ARCH.iso . && 
isohybrid ../debian-live-$ARCH.iso && 
cd ..