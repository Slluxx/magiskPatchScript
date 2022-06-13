# What does this do

It allows you to patch your boot.img for magisk root access, update your phone via sideload and flash the patched boot.img file in an automated way from your pc. This script can both be used as class and standalone software to automate the process of flashing updates and rooting afterwards.

This script will **not** give you root access from nothing. In order to use the magisk patches from your phone, it already needs to be rooted!


## Requirements

- ADB & Fastboot installed and up to date
- Working drivers for your phone to be recognized in both modes
- Root access


## How to use

You can download the script and run it via `python ./autoupdate.py`. Its tested on my device (sweet) and if your device is not added to this script, it will also use exactly that procedure. If you want to add your phone to the script, please extend the if statement at the bottom. If you want a custom procedure (for example just patching the boot.img) then include this script like a class and write your own script.

## Functions

(If used as Class, these can be mixed and matched in your script.)

- Check root status
- Get device (codename)
- Reboot to mode (recovery, bootloader, system, sideload, sideload-auto-reboot)
- Reboot from bootloader
- Wait for ADB
- Wait for bootloader
- Wait for sideload
- Wait for folder to be initialized (eg /sdcard/ after reboot)
- Sideload Zip
- Extract file from zip
- Push/patch/pull boot.img for magisk patch
- Flash boot image

## Roadmap

- Find a proper name for this repo
- Find a proper description for this repo
- Find a proper name for this script
- Make an actual good readme
- Refine script
- windows / linux binary so python does not have to be installed
- gui for noobs


## Thanks to:

- zgfg (XDA)
- ipdev (XDA)