# HY300 Pro Generic System Image (GSI) Compatibility Research

## 1. Overview
This document evaluates the compatibility of Android 11 (API Level 30) Generic System Images (GSI) on the HY300 / HY300 Pro projector platform (Allwinner H713 SoC). Testing utilized PHH Treble ARM32 A/B images flashed to the logical `system_a` partition inside `super`.

## 2. Environment Specifications
- **SoC:** Allwinner H713 (`sun50iw12p1` / `ares` platform)
- **Target Architecture:** 32-bit ARM (`armeabi-v7a`)
- **Base GSI Image:** Android 11 (API Level 30) ARM32 Binder64/VNDK-30 with PHH Treble patches
- **Graphics Pipeline:** ARM Mali-G31 GPU with proprietary Allwinner `sunxihwc` Hardware Composer
- **Display Resolution:** 1280 × 720 (60 Hz)

## 3. Technical Obstacles & Root Cause Analysis

### A. Storage Node Identifier Mismatch (`UDISK`)
- **Symptom:** System services and Zygote crashed immediately during early init; `/data` remained unpopulated.
- **Root Cause:** Standard AOSP/GSI expects `/dev/block/by-name/userdata`. The device's GPT labels this partition `UDISK` (`/dev/block/mmcblk0p26`).
- **Resolution / Workaround:** Manually binding `UDISK` to `/data` in early recovery or init scripting and triggering decryption post-mount:
  ```bash
  mount -t f2fs /dev/block/by-name/UDISK /data
  setprop vold.decrypt trigger_post_fs_data
  ```

### B. The "Mount-to-Blank" Phenomenon
- **Symptom:** 
  - When `/data` is unmounted, the display engine successfully renders the boot animation on the wall.
  - As soon as `/data` is mounted and `system_server` initializes `SystemUI` and user preferences, the projector optical engine immediately drops to "backlight only" (blank black screen).
- **Root Cause:** SurfaceFlinger attempts to negotiate display composition modes unsupported by the proprietary Allwinner HWC HAL, resulting in `waitForCommitFinish: timeout waiting for commit finish!`.

### C. Hardware Composer (HWC) & VNDK Mismatches
- **Configuration Dependencies:** The Allwinner HWC requires model-specific JSON files located at `/vendor/etc/dispconfigs/h713-tuna_p3.json`.
- **Client Creation Failures:** GSI SurfaceFlinger logs `failed to create composer client`, indicating IPC protocol mismatches between standard AOSP HIDL composer clients and Allwinner's implementation.
- **Dependency Shims:** Vendor libraries require older VNDK v28 symbols. Successfully resolved by mounting `libminijail.so` into `/vendor/lib/libminijail_vendor.so`.

### D. SystemUI Keyguard Crash Loop
- `com.android.systemui` encounters a `NullPointerException` inside `StatusBarKeyguardViewManager` because the display subsystem fails to signal active presentation status to the Window Manager.

## 4. Evaluated Workarounds & Configurations

| Parameter / Action | Configuration | Purpose |
| --- | --- | --- |
| **VNDK Shim** | Bind-mount VNDK v28 `libminijail.so` | Resolves symbol missing errors in vendor display HAL |
| **Graphics HAL Properties** | `ro.hardware.egl=mali` / `ro.hardware.gralloc=ares` | Forces explicit binding to Allwinner proprietary GPU drivers |
| **Display Geometry** | `wm size 1280x720` | Enforces native projector LCD panel resolution |
| **Provisioning Bypass** | `device_provisioned=1` / `user_setup_complete=1` | Skips AOSP SetupWizard display init sequence |

## 5. Summary Findings
- The device hardware is capable of executing AOSP Generic System Images.
- The primary blocker for daily driver GSI usage is the proprietary Allwinner `sunxihwc` display stack, which fails during frame commit handshakes with generic SurfaceFlinger.
- Complete GSI stability requires a custom SurfaceFlinger-to-HWC translation shim or an open-source DRM/KMS kernel driver port.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
