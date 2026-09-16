# HY300 Pro Boot Modes & Triggers Research

## 1. Overview
The HY300 / HY300 Pro projector platform (Allwinner H713 SoC) supports multiple operational boot modes. Control flow is evaluated during the early U-Boot execution stage prior to Android kernel loading, allowing mode selection via hardware buttons, infrared (IR) remote commands, and software triggers.

## 2. Supported Boot Modes

| Boot Mode | Target Subsystem | Entry Mechanism | Purpose |
| --- | --- | --- | --- |
| **Normal Boot** | Android OS | Default power-on | Standard user environment |
| **Recovery** | Recovery Ramdisk | Home IR key / `reboot recovery` | Device wipe and OTA flashing |
| **Fastboot** | Bootloader Fastboot | U-Boot environment script | Low-level raw partition flashing |
| **Fastbootd** | Userspace Fastboot | Recovery subservice | Dynamic partition (`super`) management |
| **FEL Mode** | Allwinner BootROM | Vol+ IR key / `fastboot oem efex` | Low-level USB flashing & unbricking |

## 3. Infrared (IR) Key Triggers in U-Boot
IR remote key monitoring is integrated directly into U-Boot before the display initializes. The bootloader polls the IR receiver register during early initialization:

- **Volume Up (`Vol+`):** Forces early exit into **Allwinner FEL Mode** (`USB ID 1f3a:efe8`).
- **Home Button:** Forces boot flow into **Recovery Mode** and triggers an automatic factory data wipe.

This early interception confirms that boot control logic resides in the bootloader rather than in the Android userspace.

## 4. Environment-Based Control (`env.fex`)
U-Boot utilizes script-driven boot commands stored in the `env` partition (`env.fex`). The primary execution strings include:

```bash
# Normal Boot command
boot_normal=sunxi_flash read 45000000 boot;bootm 45000000

# Recovery Boot command
boot_recovery=sunxi_flash read 45000000 recovery;bootm 45000000

# Fastboot trigger
boot_fastboot=fastboot

# Master entrypoint
bootcmd=run setargs_nand boot_normal
```

Modifying `bootcmd` allows persistent redirection of the default boot path, enabling automated fallback states or custom recovery redirection without binary modifications to U-Boot.

## 5. Summary Findings
- Boot modes are resolved in U-Boot prior to kernel decompression.
- Remote control IR triggers provide hardware-less access to FEL and Recovery modes.
- Scripted U-Boot environment entries (`bootcmd`) allow non-destructive boot redirection.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
