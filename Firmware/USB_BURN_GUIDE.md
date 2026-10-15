# HY300 Pro USB Burn-In & Secure Storage Anti-Rollback Guide

## 1. Overview
The HY300 / HY300 Pro projector platform (Allwinner H713 SoC, `sun50iw12p1`) features an automated firmware recovery and flashing mechanism triggered via USB storage during early boot (`auto_update_check`). However, once a firmware package is flashed, the bootloader records the build timestamp in a non-volatile **Secure Storage (SST)** key named `firmware_version`.

> [!IMPORTANT]
> **Anti-Rollback Enforcement:** If you attempt to re-flash the same firmware package or downgrade to an older release, U-Boot compares the candidate image timestamp against the Secure Storage record and silently aborts the burn process without updating partitions. Overriding or backdating this key via the U-Boot serial console is required to unlock re-flashing or downgrading.

This guide details:
1. The internal architecture of Allwinner's Secure Storage (`pst`).
2. Procedures for inspecting and backdating the stored `firmware_version` key via U-Boot.
3. USB drive partitioning, directory layout, and trigger script requirements.
4. Step-by-step cold-boot flashing execution.
5. Hardware diagnostics and troubleshooting (checksum mismatches, USB controller bus stalls, and missing display indicators).

## 2. Allwinner Secure Storage Architecture

Allwinner Board Support Packages (BSPs) utilize a dedicated persistent storage block on the eMMC managed by the bootloader's `pst` (Private Storage / Secure Storage) interface.

### Secure Storage Key Format
During the firmware burn routine, the extraction engine parses the image metadata header and commits an entry into the SST key-value store:

```text
77e893c0: 17253948 00000000 6d726966 65726177    H9%.....firmware
77e893d0: 7265765f 6e6f6973 00000000 00000000    _version........
...
77e89420: 00000014 35323032 2d39302d 30203232    ....2025-09-22 0
77e89430: 39343a39 0a31343a 00000000 00000000    9:49:41.........
```

Key structure components:
- **Magic Header & Checksum:** `0x17253948` followed by CRC validation words.
- **Key Name:** `firmware_version` (ASCII string).
- **Length:** `0x14` (20 bytes).
- **Value:** ISO timestamp string (e.g., `2025-09-22 09:49:41\n`).

During early initialization, the `auto_update_check` command validates whether the candidate `update.img` carries a timestamp strictly newer than the timestamp recorded in Secure Storage. If the image timestamp is less than or equal to the stored value, the updater declines to flash.

## 3. Inspecting and Overriding Secure Storage via U-Boot

To bypass the anti-rollback barrier, you must access the interactive U-Boot serial console via the board's UART test points (115,200 baud, 3.3V TTL; see [UART & FEL Guide](../Hardware/UART_FEL.md)).

### Step 1: Read the Existing Timestamp
At the U-Boot prompt (`=> `), query the active anti-rollback key:

```bash
pst read firmware_version
```

The bootloader displays the raw hex and ASCII representation of the recorded timestamp.

### Step 2: Backdate the Stored Timestamp
To permit re-flashing current or earlier firmware versions, overwrite the `firmware_version` key with an arbitrary historical date.

> [!WARNING]
> **Command Argument Parsing:** The U-Boot command-line parser treats whitespace as argument delimiters. Passing a timestamp with spaces (e.g., `pst write firmware_version 2000-01-01 00:00:00`) causes the parser to fail with `para error!`. You must format the value as a single, continuous hyphenated string: `2000-01-01-00:00:00`.

Execute the override command:

```bash
pst write firmware_version 2000-01-01-00:00:00
```

Expected bootloader response:
```text
Also save user data firmware_version to secure storage
sunxi secure storage has no flag
[xxx.xxx]There is the same name in the secure storage, try to erase it
[xxx.xxx]erase secure storage: 7 data only ok
[xxx.xxx]write secure storage: 7 ok
```

The anti-rollback lock is now cleared, allowing any valid firmware image to be flashed.

## 4. USB Drive Preparation & Trigger Script

The automated update engine expects a specific directory structure and command script on the first partition of an MBR-partitioned, FAT32-formatted USB flash drive.

### Drive Layout
```text
USB_ROOT (FAT32, MBR)
└── update/
    ├── auto_update.txt
    └── update.img
```

### Script Syntax (`auto_update.txt`)
Create a plain-text file named `auto_update.txt` inside the `update` directory containing the following exact syntax:

```text
sunxi_flash write update/update.img firmware
%
```

Parameter breakdown:
- **`sunxi_flash write`**: Invokes the Allwinner sprite flashing engine.
- **`update/update.img`**: Relative path to the target firmware container on the drive.
- **`firmware`**: Flashes all partition targets (GPT, bootloader, kernel, `super`, calibration).
- **`%`**: Mandatory delimiter indicating EOF (End of File) to the U-Boot script parser.

## 5. Executing the Flashing Routine

> [!CAUTION]
> **The Cold-Boot Requirement:** Manually invoking `auto_update_check` from an active interactive U-Boot console session frequently results in EHCI/USB-DRD controller lockups or bus hangs due to incomplete driver reinitialization. **Always execute the flashing process from a cold power cycle.**

### Step-by-Step Flashing Procedure:
1. Connect the prepared USB drive to the projector's rear USB-A port.
2. Connect your USB-to-UART serial adapter to monitor output via terminal emulator (115,200 baud).
3. Disconnect the 12V DC power plug from the projector.
4. Reconnect the DC power plug.
5. **Do not press any keys in the serial terminal**; allow the autoboot countdown to expire normally.
6. U-Boot executes `auto_update_check` in a clean hardware state, detects `update/auto_update.txt`, and begins flashing partitions sequentially.

## 6. Troubleshooting & Diagnostics

### A. Partition Verification Checksum Mismatch
```text
origin checksum=149ec65c, active checksum=ff379e68
sunxi sprite: part BOOT_FEX... verify error
```
- **Cause:** Data written to the eMMC failed verification against the embedded checksum inside `update.img`. This is typically caused by uncommitted buffer corruption when copying files to the USB drive.
- **Resolution:** Verify the SHA-256 hash of `update.img` between your host machine and the USB drive:
  ```powershell
  # Windows PowerShell
  Get-FileHash D:\update\update.img -Algorithm SHA256
  ```
  ```bash
  # Linux / macOS
  sha256sum /media/user/USB_DRIVE/update/update.img
  ```
  Always cleanly eject / unmount the USB drive before disconnecting it from the host computer.

### B. USB Read Speed Degradation or Bus Stalls
If data transfer rates drop significantly (e.g., decaying from `14 MiB/s` down to `< 1 MiB/s`) or freeze mid-partition:
- **Cause:** The projector's unbuffered 5V USB power rail suffers thermal sag under heavy load from high-power metal USB 3.0/3.1 flash drives.
- **Resolution:** Use a standard plastic **USB 2.0 flash drive** (8GB to 32GB capacity, formatted FAT32 with 32KB allocation unit size).

### C. Missing On-Screen Progress Bar
If the green progress bar does not appear on the projected display during flashing:
- **Cause:** An earlier failed flash or erase cleared `bootloader_a` (which houses `boot-resource.fex` and graphical display assets).
- **Resolution:** The flashing engine still operates in headless mode. Monitor the UART serial console for real-time progress percentages, block writes, and final status reporting.

## 7. Summary Findings
- Allwinner H713 firmware updates via USB rely on `auto_update_check` invoked during early U-Boot execution.
- The Secure Storage (`pst`) system enforces anti-rollback by checking image timestamps against the non-volatile `firmware_version` key.
- Anti-rollback enforcement can be completely bypassed by overwriting the key (`pst write firmware_version 2000-01-01-00:00:00`) via serial console.
- Reliable USB flashing requires an MBR FAT32-formatted USB 2.0 drive, an `auto_update.txt` script terminated with `%`, and cold-boot power cycling.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
