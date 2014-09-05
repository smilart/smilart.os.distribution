#!/bin/bash

set -vx
ID=`date +%d.%m.%y_%X`
VERSION="jessie-$ID"

#apt-get install debootstrap syslinux squashfs-tools genisoimage memtest86+ rsync gcc git-core isolinux live-boot
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

debootstrap --arch=$ARCH --variant=minbase jessie chroot http://ftp.us.debian.org/debian/
cp /etc/resolv.conf chroot/etc/resolv.conf

cp -pv ../in_chroot.sh  chroot/tmp/
cp -pv ../to_iso/autologin.c chroot/tmp
cp -pv ../to_iso/inittab chroot/etc/inittab
gcc ../to_iso/autologin.c -o chroot/usr/local/sbin/autologin
mkdir -p chroot/var/lib/smilart_srv/scripts && cp -pv ../../smilartos-install/smilartos-install.py chroot/var/lib/smilart_srv/scripts/smilartos-install.py && cp -pv ../to_iso/config_network.sh chroot/var/lib/smilart_srv/scripts/config_network.sh
cp -pv ../to_iso/after_install_to_xen.sh chroot/var/lib/smilart_srv/scripts/after_install_to_xen.sh

wget https://pypi.python.org/packages/source/u/urwid/urwid-1.2.1.tar.gz -P chroot/tmp

[[ -d /tmp/licenseencryptiontool ]] && rm -r /tmp/licenseencryptiontool
(cd /tmp && git clone git@bitbucket.org:smilart/licenseencryptiontool.git)
(cd /tmp/licenseencryptiontool/nodeinfo && make)
mkdir -p chroot/var/lib/smilart_srv/utils && cp -pv /tmp/licenseencryptiontool/nodeinfo/dist/Debug/GNU-Linux-x86/nodeinfo chroot/var/lib/smilart_srv/utils/nodeinfo


echo "Building Docker-conteiners"
mkdir -p image/{live,isolinux}
source ../repo_container.sh docker image/live
(cd image/live && split -b 1024m "repos.tar" "repos.tar.part-" && rm -fv repos.tar)

echo "Setup chroot"
chroot chroot /bin/bash -c "/tmp/in_chroot.sh $ARCH"

cp -pv ../to_iso/default.nginx chroot/etc/nginx/sites-available/default

cp -pv ../to_iso/autologin@.service  chroot/lib/systemd/system/getty@.service
cp -pv ../to_iso/.bashrc  chroot/root/.bashrc

rm -fv chroot/etc/resolv.conf
#mkdir -p image/{live,isolinux}
mksquashfs chroot image/live/filesystem.squashfs #-e boot

cp chroot/boot/vmlinuz-3.14-2-$ARCH image/live/vmlinuz1 && 
cp chroot/boot/initrd.img-3.14-2-$ARCH image/live/initrd1

sed "s/__VERSION__/$VERSION/" < ../to_iso/isolinux.cfg > image/isolinux/isolinux.cfg

[[ -f /tmp/syslinux-4.05.tar.gz ]] && rm -fv /tmp/syslinux-4.05.tar.gz
wget https://www.kernel.org/pub/linux/utils/boot/syslinux/syslinux-4.05.tar.gz -P /tmp
[[ -d /tmp/syslinux-4.05 ]] && rm -rfv /tmp/syslinux-4.05
(cd /tmp && tar xf /tmp/syslinux-4.05.tar.gz)

cp /tmp/syslinux-4.05/core/isolinux.bin image/isolinux/ && 
cp /tmp/syslinux-4.05/com32/menu/menu.c32 image/isolinux/ && 
cp /tmp/syslinux-4.05/com32/hdt/hdt.c32 image/isolinux/ && 
cp /boot/memtest86+.bin image/live/memtest

cd image && 
genisoimage -rational-rock -volid "Debian Live" -V "SMILART_OS" -cache-inodes -joliet -full-iso9660-filenames -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -output ../debian-live-$ARCH-$VERSION.iso . && 
isohybrid ../debian-live-$ARCH-$VERSION.iso && 
cd ..