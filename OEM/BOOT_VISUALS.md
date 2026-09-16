# HY300 Pro Boot Visuals Customization Research

## 1. Overview
The boot visualization pipeline on the HY300 / HY300 Pro projector operates in two distinct stages: the early bootloader splash logo and the Android userspace boot animation. Both stages can be customized independently via the `/oem` (`media_data`) partition.

## 2. Visual Pipeline Stages

### Stage 1: Bootloader Splash Screen
The splash screen is loaded by U-Boot immediately after DRAM initialization and before the Android kernel is decompressed.
- **Storage Location:** `/oem/bootlogo.bmp` (located in the FAT-formatted `media_data` partition)
- **Image Specifications:**
  - **Resolution:** 1280 × 720 pixels
  - **Format:** Windows Bitmap (BMP)
  - **Color Depth:** 24-bit RGB (uncompressed)
  - **File Size:** Exactly ~2,764,854 bytes (~2.63 MB)
- **Execution:** U-Boot reads the bitmap directly from the FAT filesystem and writes the raw pixel buffer to the display framebuffer.

### Stage 2: Android Userspace Boot Animation
The boot animation is rendered by the Android `bootanimation` binary during system service initialization.
- **Storage Location:** `/oem/media/bootanimation.zip`
- **Search Priority Order:**
  1. `/oem/media/bootanimation.zip` (highest active priority on stock firmware)
  2. `/system/media/bootanimation.zip` (stock fallback animation)
  3. `/product/media/` (contains audio and UI sound assets only)
- **Archive Format:**
  - Zip archive stored with **zero compression** (Store method / 0% compression).
  - Contains `desc.txt` defining resolution, frame rate, and loop count, followed by folder partitions (`part0/`, `part1/`) of sequenced PNG frames.

## 3. Modification Workflow

### Customizing the Splash Screen
1. Create a 1280×720 image using design software (a Photoshop template `bootlogo.psd` is provided in this directory).
2. Export as a standard 24-bit uncompressed BMP.
3. Replace `/oem/bootlogo.bmp` on the device or inside the `media_data` partition image.

### Customizing the Boot Animation
1. Assemble PNG frame sequences into designated folders (`part0/`).
2. Construct `desc.txt`:
   ```text
   1280 720 30
   p 1 0 part0
   p 0 0 part1
   ```
3. Archive without compression:
   ```bash
   zip -0 -r bootanimation.zip desc.txt part0 part1
   ```
4. Place the archive in `/oem/media/bootanimation.zip`.

## 4. Security Verification
The `media_data` partition is formatted as FAT and is **not protected by Android Verified Boot (AVB) or dm-verity**. Modifying or replacing these assets does not trip tamper flags or trigger boot loops.

## 5. Summary Findings
- The boot splash (`bootlogo.bmp`) is rendered by U-Boot before the kernel boots.
- `/oem/media/bootanimation.zip` takes precedence over `/system/media/bootanimation.zip`.
- Because `/oem` is unverified FAT storage, visuals can be modified safely without signing keys.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
