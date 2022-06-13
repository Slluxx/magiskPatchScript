import subprocess, zipfile, time
from os.path import exists
from os import remove


"""
Author: 
    Slluxx

Description: 
    This script can be used to automate the process of updating your phone 
    as well as restoring magisk root access by extracting the boot.img file, 
    sending it to the phone, using magisk scripts to patch it and then 
    downloading and flashing the patched image. I needed this because of 
    some sdcard raid mode shenanigans that I had to deal with which made OTA
    updates impossible. Its probably also faster to download the update on 
    your pc and use this script instead of doing it on the phone (and with magisk).

DISCLAIMER:
    This script is provided as-is. I am not responsible for any damage that 
    may occur to your phone. Use at your own risk. This script does not make 
    everything noob proof. You can break stuff and possibly brick your phone 
    if you don't know what you are doing. Also, it does not check most of the 
    ADB commands returns. There might be something wrong without even alerting
    you in the first place. You have been warned.
"""



class Phone():
    def __init__(self, initPath="/sdcard/", noRootError="inaccessible or not found"):
        self.initPath = initPath # the folder that needs to be initialized after reboot, accessible WITHOUT root.
        self.noRootError = noRootError # "adb shell su -c ls" error substring
        self.defaultDecode = 'utf-8'
        self.sdInitialized = False
        self.device = None

    def getDevice(self):
        # adb shell getprop ro.product.device
        device =  subprocess.run(['adb', 'shell', 'getprop', 'ro.product.device'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)
        device = device.split("\n")[0].strip()
        self.device = device
        return device


    def waitForFolderInit(self):
        print("Waiting for folder to be initialized")
        print("You might have to unlock your phone and wait a minute.")
        while self.sdInitialized == False:
            ret = subprocess.run(['adb', 'shell', 'ls', f'{self.initPath}'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode(self.defaultDecode)
            if ret == "":
                time.sleep(2)
            else:
                self.sdInitialized = True
        return True

    def waitForBootloaderInit(self):
        print("Waiting for bootloader to be initialized")
        ret = ""
        while ret == "":
            ret = subprocess.run(['fastboot', 'devices', '-l'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode(self.defaultDecode)
            time.sleep(2)
        return True
    
    def checkRootStatus(self):
        print("Checking if device is rooted")
        ret = subprocess.run(['adb', 'shell', 'su', '-c', 'ls', '/'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE ).stderr.decode(self.defaultDecode)
        if f"{self.noRootError}" in ret:
            return False
        else:
            return True

    def checkAdbFastbootStatus(self):
        print("Checking if adb and Fastboot are installed")
        try: 
            subprocess.run(['adb'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            return False
        
        try:
            subprocess.run(['fastboot'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            return False

    def waitForAdb(self):
        print("Waiting for a device to be connected")
        subprocess.run(['adb', 'wait-for-device'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)
    
    def waitForSideload(self):
        print("You might have to browse to (adb) 'sideload' in your recovery menu")
        subprocess.run(['adb', 'wait-for-sideload'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)
    
    def rebootToMode(self, mode):
        """Reboots the phone into a given mode.
        modes: recovery, bootloader, system, sideload, sideload-auto-reboot
        """
        print(f"Rebooting to {mode} mode")
        subprocess.run(['adb', 'reboot', f'{mode}'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)

    def sideloadZip(self, updateFile):
        if not exists(updateFile):
            print("No update file found, stopping.")
            exit()

        print(f"Sideloading {updateFile}")
        subprocess.run(['adb', 'sideload', f'{updateFile}'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)
        print("Sideloading is complete. If your phone is not restarting, click on 'restart' (to system) in your recovery menu.")

    def extractFileFromZip(self, zipFile, fileName):
        print(f"Extracting {fileName} from {zipFile}")
        if exists(zipFile):
            try:
                with zipfile.ZipFile(zipFile, 'r') as zip_ref:
                    zip_ref.extract(fileName)
            except Exception as e:
                print(f"Error extracting {fileName} from {zipFile}")
                print(e)
        else:
            print(f"{zipFile} does not exist")
            exit()

    def pushPatchPullForMagisk(self, magiskPath="/data/adb/magisk/"):
        if not exists("./boot.img"):
            print("No boot.img found, stopping.")
            exit()

        print("pushing boot.img to sd")
        subprocess.run(['adb', 'push', './boot.img', f'{self.initPath}'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)

        print("patching boot.img on system")
        subprocess.run(['adb', 'shell', 'su', '-c', f'{magiskPath}boot_patch.sh', f'{self.initPath}boot.img'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)

        print("Moving new-boot.img to pullable location")
        subprocess.run(['adb', 'shell', 'su', '-c', 'mv', f'{magiskPath}new-boot.img', f'{self.initPath}'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)

        print("pulling new-boot.img")
        subprocess.run(['adb', 'pull', f'{self.initPath}new-boot.img'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)

        if not exists("./new-boot.img"):
            print("No new-boot.img found, stopping.")
            exit()

    def flashBootImage(self, bootImagePath="./new-boot.img"):
        print("flashing new-boot.img")
        subprocess.run(['fastboot', 'flash', 'boot', f'{bootImagePath}'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)
    
    def fastbootReboot(self):
        print("rebooting to system")
        subprocess.run(['fastboot', 'reboot'], stdout=subprocess.PIPE).stdout.decode(self.defaultDecode)

    def cleanupLocal(self):
        print("Cleaning up local files")
        if exists("./new-boot.img"):
            remove("./new-boot.img")
        if exists("./boot.img"):
            remove("./boot.img")


if __name__ == "__main__":
    phone = Phone()
    if phone.checkAdbFastbootStatus() == False:
        print("ADB and/or Fastboot are not installed or not in the PATH")
        exit()

    phone.waitForAdb()
    phone.getDevice()
    if phone.checkRootStatus() == False:
        print("No root access found but is required. Please root your phone and try again.")
        exit()


    if phone.device == "sweet":
        phone.waitForFolderInit()
        phone.extractFileFromZip("update.zip", "boot.img")
        phone.pushPatchPullForMagisk()
        phone.rebootToMode("sideload-auto-reboot")
        phone.waitForSideload()
        phone.sideloadZip("update.zip")
        phone.waitForAdb()
        phone.rebootToMode("bootloader")
        phone.waitForBootloaderInit()
        phone.flashBootImage()
        phone.fastbootReboot()

    else:
        phone.waitForFolderInit()
        phone.extractFileFromZip("update.zip", "boot.img")
        phone.pushPatchPullForMagisk()
        phone.rebootToMode("sideload")
        phone.waitForSideload()
        phone.sideloadZip("update.zip")
        phone.waitForAdb()
        phone.rebootToMode("bootloader")
        phone.waitForBootloaderInit()
        phone.flashBootImage()
        phone.fastbootReboot()

    phone.cleanupLocal()
    print("Done!")