#! /bin/bash

set -vx
if [ -z "$1" ]; then
    ARCH="amd64"
else
    ARCH=$1
fi
mount none -t proc /proc && 
mount none -t sysfs /sys && 
mount none -t devpts /dev/pts && 
export HOME=/root && 
export LC_ALL=C && 
apt-get install dialog dbus --yes && 
dbus-uuidgen > /var/lib/dbus/machine-id && 
apt-get update --yes

echo "debian-live-smilart" > /etc/hostname

apt-get install --no-install-recommends --yes \
linux-image-3.14-2-$ARCH live-boot \
net-tools wireless-tools wpagui tcpdump wget ca-certificates openssh-server openssh-client iputils-ping inetutils-tools nginx \
pciutils usbutils gparted hfsprogs rsync dosfstools syslinux partclone nano pv python2.7 python2.7-dev mc bzip2 parted

export DEBIAN_FRONTEND=noninteractive
apt-get -q -y install console-cyrillic

tar -xzf /tmp/urwid-1.2.1.tar.gz -C /tmp
(cd /tmp/urwid-1.2.1 && /usr/bin/python2.7 setup.py install)
mkdir -pv /var/lib/smilart_srv/coreos/amd64-usr/current
wget https://raw.githubusercontent.com/coreos/init/master/bin/coreos-install -P /var/lib/smilart_srv/coreos
wget http://stable.release.core-os.net/amd64-usr/current/coreos_production_image.bin.bz2 -P /var/lib/smilart_srv/coreos/amd64-usr/current
wget http://stable.release.core-os.net/amd64-usr/current/coreos_production_image.bin.bz2.sig -P /var/lib/smilart_srv/coreos/amd64-usr/current/
chmod +x /var/lib/smilart_srv/coreos/coreos-install

echo -e "smilart\nsmilart" | passwd root
echo "127.0.0.1		stable.release.core-os.net" >> /etc/hosts

rm -f /var/lib/dbus/machine-id && 
apt-get clean && 
#rm -rf /tmp/* && 
umount -lf /proc && 
umount -lf /sys && 
umount -lf /dev/pts
