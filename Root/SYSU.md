# HY300 Pro Custom su Utility (`sysu`)

## 1. Overview
The `sysu` utility is a lightweight, standalone `su` implementation developed for the Allwinner H713 platform. It serves as a persistent root binary within `/system/bin` or a recovery ramdisk to guarantee root access independently of Magisk daemon lifecycle.

## 2. Source Code & Compilation
The tool is compiled statically to avoid dynamic linker and library version dependencies:

- **Source File:** `sysu.c`
- **Compiler:** GNU ARM cross-toolchain (`arm-linux-gnueabi-gcc`)
- **Compilation Command:**
  ```bash
  arm-linux-gnueabi-gcc -static -O2 sysu.c -o sysu
  arm-linux-gnueabi-strip sysu
  ```
- **Target Architecture:** ARMv7-A (32-bit little-endian) to match the Android 32-bit userspace.

## 3. Installation & Permissions
When deploying to a writable system partition (`/system/bin/`):

```bash
# Copy binary
cp sysu /system/bin/sysu

# Enable SetUID and SetGID bits
chmod 6755 /system/bin/sysu
chown root:root /system/bin/sysu

# Assign unconfined SELinux execution context
chcon u:object_r:su_exec:s0 /system/bin/sysu
```

Optional convenience alias:
```bash
ln -s /system/bin/sysu /system/bin/debugroot
```

## 4. Operational Behavior
Unlike the vendor `/system/bin/wifi` helper, `sysu`:
- Does not drop Linux POSIX capabilities.
- Spawns an unrestricted interactive shell (`/system/bin/sh`) as UID 0 / GID 0.
- Operates reliably as an emergency backdoor across reboots.

## 5. Summary Findings
- Statically linked ARMv7-A executable ensures cross-compatibility with Android 11.
- `6755` permissions combined with `u:object_r:su_exec:s0` provide unrestricted root shell transition.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
