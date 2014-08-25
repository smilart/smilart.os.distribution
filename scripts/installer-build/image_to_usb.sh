#!/bin/bash

SOURCE=$1 
DEVICE=$2

# image_to_usb ./debian-live-amd64.iso /dev/sdb

dd if=$SOURCE of=$DEVICE