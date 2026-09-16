# HY300 Pro Partition Layout & Storage Architecture

## 1. Overview
The HY300 / HY300 Pro projector utilizes an 8GB Toshiba eMMC storage device (`/dev/block/mmcblk0`, ~7.28 GiB / 7,818,182,656 bytes). The storage scheme employs a standard GPT partition table with a Virtual A/B layout and dynamic partitions managed via the Android `super` container.

> [!IMPORTANT]
> **Virtual A/B Slot Behavior:** Although the GPT table defines dual `_a` and `_b` partitions, **only slot `_a` is functional and bootable**. The standby `_b` slots (`boot_b`, `vendor_boot_b`, `dtbo_b`, `vbmeta_b`, etc.) are dummy entries that are completely zero-filled (`0x00`) or unpopulated in stock factory firmware. Switching active slots to `_b` will result in a hard brick/boot failure.

## 2. Physical Partition Table (`/dev/block/by-name/`)

| Partition | Block Device | Filesystem / Format | Status / Description |
| --- | --- | --- | --- |
| `bootloader_a` | `mmcblk0p1` | Raw / FAT | U-Boot SPL and primary bootloader (Slot A - Functional) |
| `bootloader_b` | `mmcblk0p2` | Raw / FAT | Standby slot (Zero-filled / Non-bootable) |
| `env_a` | `mmcblk0p3` | Raw (`env.fex`) | U-Boot environment variables (Slot A - Functional) |
| `env_b` | `mmcblk0p4` | Raw (`env.fex`) | Standby slot (Zero-filled / Inactive) |
| `boot_a` | `mmcblk0p5` | Android Boot Img (64 MB) | Linux kernel and initial boot ramdisk (Slot A - Active) |
| `boot_b` | `mmcblk0p6` | Android Boot Img (64 MB) | Standby slot (Empty / Zero-filled dummy) |
| `vendor_boot_a` | `mmcblk0p7` | Android Vendor Boot | Vendor ramdisk and device tree overlays (Slot A - Active) |
| `vendor_boot_b` | `mmcblk0p8` | Android Vendor Boot | Standby slot (Empty / Zero-filled dummy) |
| `super` | `mmcblk0p9` | Android Dynamic Container | Physical container hosting dynamic logical volumes |
| `misc` | `mmcblk0p10` | Raw | BCB (Bootloader Control Block) & recovery triggers |
| `vbmeta_a` | `mmcblk0p11` | AVB 2.0 | Android Verified Boot root metadata (Slot A - Active) |
| `vbmeta_b` | `mmcblk0p12` | AVB 2.0 | Standby slot (Zero-filled dummy) |
| `vbmeta_system_a` | `mmcblk0p13` | AVB 2.0 | System descriptor metadata (Slot A - Active) |
| `vbmeta_system_b` | `mmcblk0p14` | AVB 2.0 | Standby slot (Zero-filled dummy) |
| `vbmeta_vendor_a` | `mmcblk0p15` | AVB 2.0 | Vendor descriptor metadata (Slot A - Active) |
| `vbmeta_vendor_b` | `mmcblk0p16` | AVB 2.0 | Standby slot (Zero-filled dummy) |
| `frp` | `mmcblk0p17` | Raw (512 KB) | Factory Reset Protection; offset `0x7FFFF` holds unlock flag |
| `empty` | `mmcblk0p18` | Raw | Reserved partition |
| `metadata` | `mmcblk0p19` | ext4 | Encryption keys and Virtual A/B state |
| `private` | `mmcblk0p20` | Raw | Allwinner vendor security and calibration keys |
| `dtbo_a` | `mmcblk0p21` | DTBO | Device Tree Blob Overlay (Slot A - Active) |
| `dtbo_b` | `mmcblk0p22` | DTBO | Standby slot (Zero-filled dummy) |
| `media_data` | `mmcblk0p23` | FAT (~272 MB) | Mounted as `/oem`; stores splash logo, bootanimation, `config.ini` |
| `Reserve0_a` | `mmcblk0p24` | FAT | Vendor reserve partition (Slot A) |
| `Reserve0_b` | `mmcblk0p25` | FAT | Standby slot (Zero-filled dummy) |
| `userdata` / `UDISK` | `mmcblk0p26` | f2fs (~5.2 GB) | User application storage mounted at `/data` |

## 3. Dynamic Logical Partitions (`super`)
The `super` physical partition (`mmcblk0p9`) encapsulates logical Android filesystems exposed via Device Mapper (`dm`). Because only slot `_a` is populated, dynamic partitions map directly to slot `_a` images:

- `/dev/block/dm-0`: Mounted at `/` (`system_a`, ext4, read-only)
- `/dev/block/dm-1`: Mounted at `/vendor` (`vendor_a`, ext4, read-only)
- `/dev/block/dm-2`: Mounted at `/product` (`product_a`, ext4, read-only)

## 4. Key Runtime Mount Points

```text
/dev/block/dm-0         /          ext4    ro,seclabel,nodev,noatime
/dev/block/dm-1         /vendor    ext4    ro,seclabel,nodev,noatime
/dev/block/dm-2         /product   ext4    ro,seclabel,nodev,noatime
/dev/block/mmcblk0p26   /data      f2fs    rw,seclabel,nosuid,nodev,noatime
/dev/block/mmcblk0p19   /metadata  ext4    rw,seclabel,nosuid,nodev,noatime
/dev/block/mmcblk0p23   /oem       vfat    rw,context=...,fmask=0000,dmask=0000
```

## 5. Summary Findings
- The eMMC storage uses a 26-partition GPT configuration.
- The A/B partition scheme is **Virtual A/B in name only**: only slot `_a` contains valid, bootable partition images. All `_b` slots are fake/zero-filled placeholders.
- Modifying or flashing boot components must always target the active `_a` slot partitions (`boot_a`, `vendor_boot_a`, `dtbo_a`, `vbmeta_a`).
- System partitions exist strictly inside `super` as device-mapper volumes mapped to slot `_a`.
- `/oem` (`media_data`) is formatted as standard FAT and lacks dm-verity or AVB protection.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
