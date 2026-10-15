# HY300 Pro (Magcubic) – Allwinner H713 Research Documentation

*Maintained by **[Yuuji Lab](https://github.com/YuujiLab)**.*

## 1. Overview
This repository serves as the central engineering documentation and technical research base for the **HY300 / HY300 Pro / HY300 Pro+** projector platform, powered by the **Allwinner H713 SoC (`sun50iw12p1`)**.

The investigation spans the complete system stack: low-level BootROM (BROM) execution, U-Boot bootloader reverse engineering, UART serial debugging, Android Verified Boot (AVB) bypasses, dynamic partition architecture, userspace `fastbootd` binary patching, recovery exploits, and OEM customization.

## 2. Device Specifications
- **SoC:** Allwinner H713 (`sun50iw12p1` / TV303 platform)
- **CPU:** Quad-core ARM Cortex-A53
- **GPU:** ARM Mali-G31 MP2
- **RAM:** 1GB DDR3 SDRAM (4x 2Gb ICs: 2x Elpida J2108BCSE top + 2x Samsung K4B2G0846D bottom)
- **Storage:** 8GB Kioxia / Toshiba eMMC 5.1 (`THGBMHG6C1LBAIL`)
- **PMIC:** A8038S multi-phase power management IC
- **Audio:** XA8870C Class-D/AB audio amplifier
- **Wireless:** AIC8800D40 (Wi-Fi 6 802.11ax + Bluetooth 5.4 Dual-Mode)
- **Operating System:** Android 11 (API Level 30)
- **Kernel:** Linux 4.9.170 (ARM64 Kernel)
- **Userspace ABI:** 32-bit (`armeabi-v7a`)
- **Partition Layout:** 26-partition GPT with Virtual A/B (Slot A functional; Slot B fake/zero-filled) and dynamic partitions (`super`)

## 3. Documentation Index

### [Hardware Research](Hardware/README.md)
Teardown inspection and physical debugging interfaces:
- **[PCB Inspection](Hardware/PCB_INSPECTION.md):** Silicon identification, pinouts, and test pad locations.
- **[UART Console & FEL](Hardware/UART_FEL.md):** 115,200 baud 3.3V serial console configuration and BootROM FEL triggers.
- **[UART Session Log](Hardware/uart_log.txt):** Raw captured U-Boot terminal session and environment dump.

### [FEL & BootROM Research](FEL/README.md)
Low-level silicon execution and unbricking procedures:
- **[FEL & BROM Research](FEL/FEL_RESEARCH.md):** 40KB BootROM memory map, boot flow sequence, SRAM `0x0010C000` resolution, H713 support in `sunxi-tools` ([YuujiLab/sunxi-tools](https://github.com/YuujiLab/sunxi-tools)), 1024MB DDR3 initialization, and direct U-Boot execution.

### [Boot Process & Security](Boot/README.md)
Early boot chain analysis and bootloader modifications:
- **[Boot Modes & Triggers](Boot/BOOT_MODES.md):** IR remote triggers (`Vol+` for FEL, `Home` for Recovery) and environment scripts.
- **[Fastboot & Security Research](Boot/FASTBOOT_RESEARCH.md):** AVB status, Fastboot HAL OEM commands (`efex`), and userspace `fastbootd` Ghidra binary patch (`0x28cc8`).
- **[U-Boot Reverse Engineering](Boot/UBOOT_RESEARCH.md):** Disassembly findings, linker command tables, and script-driven boot control.

### [Firmware Analysis & Flashing](Firmware/README.md)
Partition structure, raw storage acquisition, and offline USB flashing:
- **[Partition Layout & GPT](Firmware/PARTITION_LAYOUT.md):** Complete 26-partition map, Virtual A/B architecture (Slot A functional, Slot B fake/zero-filled), dynamic volumes, and runtime mounts.
- **[System Firmware Analysis](Firmware/SYSTEM_ANALYSIS.md):** Build fingerprint, engineering tools, permissive SELinux, and hidden `/system/bin/wifi` UART SUID root binary.
- **[eMMC Firmware Extraction](Firmware/EMMC_DUMPING.md):** Raw 7.8GB eMMC partition dumping via unprivileged ADB (no root required), GPT verification, and carving.
- **[USB Burn-In & Secure Storage](Firmware/USB_BURN_GUIDE.md):** Automated USB recovery flashing (`auto_update_check`), Allwinner Secure Storage (`pst`) anti-rollback bypass, timestamp backdating, and sprite engine troubleshooting.

### [Recovery & Exploit Chains](Recovery/README.md)
Recovery subsystem reverse engineering and automated payload delivery:
- **[Recovery Exploit Research](Recovery/RECOVERY_RESEARCH.md):** Disabling modern A/B `payload.bin` enforcement (`0x00030220` branch patch), dynamic partition loopback mapping, automated `build_super.py` repack helper, and headless root injection.

### [Rooting & Privilege Escalation](Root/README.md)
Techniques for persistent root access:
- **[Magisk Rooting Guide](Root/MAGISK_GUIDE.md):** Fully self-contained root guide; extracting `boot_a` via unprivileged ADB (no root required), Magisk patching, fastboot flashing, and restoration.
- **[Custom su Binary (`sysu`)](Root/SYSU.md):** Statically compiled ARMv7 root binary, permissions (`6755`), and SELinux contexts.
- **[Vendor Root Helper Analysis](Root/wifi/README.md):** Reverse engineering `/system/bin/wifi` SUID wrapper, UART console root execution, and ADB privilege restrictions.

### [OEM Customization](OEM/README.md)
Non-destructive branding and feature modification:
- **[OEM Partition Customization](OEM/CUSTOMIZATION.md):** Architecture of `/oem` (`media_data`), `config.ini` feature flags, and `customer.prop` property overrides.
- **[Boot Visuals Customization](OEM/BOOT_VISUALS.md):** 1280x720 24-bit BMP splash logo and `/oem/media/bootanimation.zip` override pipeline.

### [Generic System Image (GSI)](GSI/README.md)
Custom AOSP ROM compatibility testing:
- **[GSI Compatibility Discoveries](GSI/GSI_DISCOVERIES.md):** Android 11 Treble testing, `UDISK` userdata naming mismatch, and Allwinner Hardware Composer (`sunxihwc`) display analysis.

### [OTA Updates & Protocols](OTA%20Updates/README.md)
Update protocol reverse engineering:
- **[Active OTA Research](OTA%20Updates/HtcOtaUpdate_QZ_RESEARCH.md):** `triplesai.com` JSON API and SHA1 signature algorithm.
- **[Legacy OTA Research](OTA%20Updates/OTA_RESEARCH.md):** `bigbigcloud.cn` (DeviceHive) protocol analysis.

## 4. Research Milestones Summary
- [x] Full raw 7.8GB eMMC firmware backup acquired and verified.
- [x] Hardware UART serial console confirmed and operational (115,200 baud, 3.3V).
- [x] BootROM reverse-engineered; direct USB FEL bring-up with DDR3 initialization verified.
- [x] Magisk systemless root confirmed stable on Android 11 (`boot_a` dumped directly via unprivileged ADB without root).
- [x] Userspace `fastbootd` lock patched via Ghidra (`0x28cc8`), enabling logical partition writes.
- [x] Stock recovery patched (`0x00030220`) to restore legacy ZIP execution and dynamic partition loop-mounting.
- [x] Complete 26-partition GPT hierarchy mapped; Virtual A/B reality confirmed (Slot A active, Slot B fake/zero-filled).
- [x] Unverified `/oem` partition leveraged for custom splash screens, boot animations, and branding.
- [x] Allwinner Secure Storage (SST / `pst`) anti-rollback mechanism bypassed, enabling USB burn-in flashing and version downgrading.
- [x] OTA communication protocol reverse-engineered with working verification tools.

## 5. Disclaimer & Liability Waiver

The procedures, scripts, tools, and research documentation contained in this repository are provided strictly for educational, engineering, and security research purposes. 

- **User Responsibility:** Modifying flash partitions, bootloaders, or low-level system firmware carries an inherent risk of soft-bricking, bootlooping, or permanently damaging (hard-bricking) your hardware. By following any guides or executing any commands found here, you assume sole responsibility for the outcome.
- **No Warranty or Support Guarantee:** All materials are provided "as-is" without warranty of any kind, express or implied. The authors and contributors are not responsible for bricked devices, lost data, failed hardware, or voided warranties. Direct troubleshooting support is not guaranteed.
- **Hardware Variation Notice:** White-label hardware platforms (including Magcubic / HY300 variants) frequently change board layouts, eMMC chips, and partition structures across production batches without notice. Always verify your own device's partition offsets and back up your complete raw storage (`mmcblk0`) before modifying any partition.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
