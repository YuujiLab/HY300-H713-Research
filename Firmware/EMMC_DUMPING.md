# HY300 Pro eMMC Firmware Extraction & Dumping

## 1. Overview
This guide documents the procedures for obtaining bit-exact physical dumps of the onboard 8GB eMMC flash memory and individual partitions on the HY300 / HY300 Pro projector (Allwinner H713 SoC). 

> [!TIP]
> **No Root Required for Extraction:** Testing confirms that unprivileged ADB shell sessions (`uid=2000`) retain direct read access to `/dev/block/` block devices and `/dev/block/by-name/` nodes due to permissive SELinux rules and open device permissions. **The `su` binary is NOT required to dump partitions or the complete eMMC image.**

## 2. Storage Geometry & Sector Layout
- **Device Node:** `/dev/block/mmcblk0`
- **Total Sectors:** 15,269,888 sectors (512 bytes/sector)
- **Calculated Capacity:** Exactly 7,818,182,656 bytes (~7.28 GiB)
- **Sector Verification Commands:**
  ```bash
  adb shell cat /proc/partitions | grep mmcblk0
  adb shell cat /sys/block/mmcblk0/size
  ```

## 3. Full Raw Image Extraction

### Method A: Streaming Directly over ADB to Host (No Root Required)
Stream the raw block device across an ADB tunnel directly to a host workstation:
```bash
adb exec-out "dd if=/dev/block/mmcblk0 bs=1M status=none" > emmc_full.img
```

### Method B: Dumping to Connected USB Storage
If a FAT32 or NTFS formatted USB storage drive is connected to the projector:
```bash
adb shell "dd if=/dev/block/mmcblk0 of=/storage/USB_DRIVE_ID/emmc_full.img bs=1M status=progress"
```
Expected output upon completion: `7818182656 bytes (7.8 GB, 7.3 GiB) copied`.

## 4. Dumping Individual Partitions Directly
Rather than carving from a full 7.8GB image, individual partitions can be dumped directly by name over unprivileged ADB:
```bash
# Dump boot_a partition directly to host
adb exec-out "dd if=/dev/block/by-name/boot_a bs=1M status=none" > boot_a.img

# Or dump directly to device storage (/sdcard)
adb shell "dd if=/dev/block/by-name/boot_a of=/sdcard/Download/boot_a.img bs=1M"
```

## 5. Verification & Partition Inspection
Validate the dump integrity on a Linux workstation using GPT utilities:
```bash
gdisk -l emmc_full.img
```
Confirm the GPT header reports valid backup tables at the end of the image and lists partitions `bootloader_a` through `userdata` without corruption.

## 6. Carving Specific Partitions
If extracting from a full image instead of live dumping:
```bash
# Example: Carve boot_a (Start sector 205824, size 64MB = 131072 sectors of 512 bytes)
dd if=emmc_full.img of=boot_a.img bs=512 skip=205824 count=131072
```

## 7. Summary Findings
- Full eMMC images measure exactly 7,818,182,656 bytes.
- Standard ADB shell sessions have direct read access to `/dev/block/mmcblk0` and `/dev/block/by-name/*` without root (`su`).
- Individual partitions such as `boot_a` can be extracted directly over ADB for Magisk patching on completely unrooted stock devices.
- Backing up `mmcblk0` ensures full recovery capability via FEL mode or fastboot.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
