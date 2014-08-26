#! /bin/bash

mount LABEL=EFI-SYSTEM /mnt
echo "DEFAULT coreos.A" > /mnt/syslinux/default.cfg
umount /mnt