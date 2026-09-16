# HY300 Pro OEM Customization & Branding Research

## 1. Overview
The HY300 / HY300 Pro projector platform uses an independent `/oem` partition backed by the physical `media_data` block partition (`/dev/block/mmcblk0p23`). The partition is formatted as standard FAT (~272 MB) and is **not protected by Android Verified Boot (AVB) or dm-verity**. This architecture enables white-label OEM customization, feature toggling, and visual branding modifications without tripping boot integrity mechanisms.

## 2. Partition Structure & Hierarchy
Directory structure of the mounted `/oem` filesystem:

```text
/oem/
├── bootlogo.bmp             # 1280x720 24-bit uncompressed BMP (U-Boot splash)
├── config.ini               # Runtime hardware and UI feature toggles
├── customer.prop            # Android system property overrides & branding
├── shortcuts.config         # Vendor launcher shortcut configuration
├── magic.bin                # Vendor hardware activation token / identifier
├── spectraos/
│   └── brand_logo.png       # UI launcher branding logo
└── media/
    └── bootanimation.zip    # Android userspace boot animation archive
```

## 3. Configuration & Runtime Feature Flags (`config.ini`)
The vendor firmware parses `config.ini` at boot to enable or disable hardware subsystems and UI options dynamically:

| Parameter Key | Subsystem | Functionality Description |
| --- | --- | --- |
| `autoKeystone` | Display / Sensor | Enables automatic keystone angle correction via accelerometer |
| `manualKeystone` | Display / UI | Exposes manual 4-point corner calibration screen in Settings |
| `screenZoom` | Display Engine | Enables optical scaling and digital screen reduction |
| `bluetooth` | Wireless HAL | Initializes Bluetooth stack and pairing menus |
| `network` | Wi-Fi HAL | Controls Wi-Fi scanning and settings presentation |
| `hdmiCEC` | Video Input | Enables HDMI Consumer Electronics Control pass-through |
| `developerMode` | System UI | Forces Developer Options menu visibility in Settings |
| `systemUpdate` | OTA Client | Controls visibility of online and local update menus |
| `fanLevel` | Thermal Control | Sets active PWM cooling profile and acoustic thresholds |
| `screenSaver` | Display Management | Timeout idle interval before blanking projection engine |

## 4. Branding & Device Identity (`customer.prop`)
Properties set in `customer.prop` override defaults defined in `/system/build.prop`:

```ini
persist.sys.deviceName=HY300 Pro+
persist.sys.modelName=HY300PRO
persist.sys.prj_device_name=Projector-BT
persist.sys.wifiApName=Projector-Hotspot
ro.miracast.name=Projector-Cast
persist.sys.Channel=HY200Pro_en_MagcubicOS_public_EMMC_cyh
persist.sys.storechannel=magcubic
```

These parameters govern the broadcast name for Miracast/AirPlay screen casting, Bluetooth speaker discovery, Wi-Fi hotspot SSID, and OTA update channel matching.

## 5. Visual Customization Pipeline
- **Bootloader Splash (`bootlogo.bmp`):** 1280 × 720 resolution, 24-bit uncompressed Windows BMP. Rendered directly by U-Boot.
- **Boot Animation (`media/bootanimation.zip`):** Uncompressed ZIP archive (`zip -0`) containing `desc.txt` and frame sequences. Takes priority over `/system/media/bootanimation.zip`.
- **Launcher Branding (`spectraos/brand_logo.png`):** Transparent PNG icon loaded by the custom Android launcher.

## 6. Flashing & Image Generation Workflow
The raw FAT filesystem image (`media_data.fat`, ~272 MB) contains mostly zeroed allocation blocks. It can be converted into an Android sparse image for fastboot deployment:

```bash
# Convert raw FAT partition to Android sparse image
img2simg media_data.fat media_sparse.img

# Flash via Fastboot
fastboot flash media_data media_sparse.img

# Decompress sparse image back to raw for loopback mounting
simg2img media_sparse.img media_data_restored.fat
```

### Verified Flashing Output & Real-World Timing
While converting to a sparse image drastically cuts USB transmission time down to sub-second levels, the onboard eMMC write speed remains the bottleneck:

```text
PS > fastboot flash media_data .\media_sparse.img
Warning: skip copying media_data image avb footer due to sparse image.
Sending 'media_data' (9992 KB)                     OKAY [  0.347s]
Writing 'media_data'                               OKAY [742.722s]
Finished. Total time: 743.137s
```

> **Important Timing Note:** Although transmitting the ~9.7 MB sparse image takes only **0.347 seconds**, writing and unsparsing the partition across the physical flash blocks takes approximately **742.7 seconds (~12.4 minutes)**. Do not disconnect power or interrupt USB communication during this period; the fastboot client is actively flashing.

## 7. Summary Findings
- The `/oem` partition provides an unverified, writable entry point for custom branding.
- `config.ini` provides runtime control over optical, thermal, and connectivity features.
- Visual assets can be replaced safely without modifying dynamic Android system partitions.
- Fastboot flashing of `media_data` requires ~12.4 minutes for the write stage to complete.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
