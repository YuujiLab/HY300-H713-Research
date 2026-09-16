# HY300 Pro OEM Customization & Branding Architecture

## 1. Overview
This directory documents the vendor customization framework on the HY300 / HY300 Pro projector platform (Allwinner H713 SoC). Customizations are isolated within the dedicated `/oem` (`media_data`) FAT partition, allowing modifications without altering verified Android system partitions.

## 2. Documentation Index

| Document | Focus Area | Key Topics |
| --- | --- | --- |
| **[CUSTOMIZATION.md](CUSTOMIZATION.md)** | OEM Architecture | Directory structure, `config.ini` feature flags, `customer.prop` branding overrides, and sparse image fastboot flashing |
| **[BOOT_VISUALS.md](BOOT_VISUALS.md)** | Visual Customization | 1280x720 24-bit BMP splash logo creation and uncompressed `bootanimation.zip` structure |

## 3. Customization Architecture
- Customizations live entirely on the unverified FAT `/oem` (`media_data`) partition.
- Asset and property modifications do not alter system integrity or trigger AVB verity checks.
- Users can build and deploy custom `media_data` sparse images using the step-by-step documentation.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
