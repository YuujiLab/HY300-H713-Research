# HY300 Pro OTA Firmware Update Research

## 1. Overview
This directory contains reverse engineering documentation for the over-the-air (OTA) update mechanisms used by the HY300 / HY300 Pro projector platform (Allwinner H713 SoC). The firmware includes two distinct update subsystems: the primary vendor client (`HtcOtaUpdate_QZ`) and a secondary Allwinner legacy client (`com.softwinner.update`).

## 2. Documentation Index

| Document | Focus Area | Status / State |
| --- | --- | --- |
| **[HtcOtaUpdate_QZ_RESEARCH.md](HtcOtaUpdate_QZ_RESEARCH.md)** | Active OTA Client (`triplesai.com` API) | Primary active update service on device |
| **[OTA_RESEARCH.md](OTA_RESEARCH.md)** | Legacy OTA Client (`bigbigcloud.cn` API) | Inactive / legacy Allwinner service |

## 3. Subsystem Findings Summary

### Primary Path (`HtcOtaUpdate_QZ`)
The primary updater is package `HtcOtaUpdate_QZ`:
- Communicates with `http://ota.triplesai.com:8080` over REST/JSON.
- Authentication: Requires a `Sign` header generated via SHA1 hash of alphabetically sorted JSON keys.
- Validation: Endpoint `POST /V1/Ota/Check` responds with `Code: 0` (update available), `Code: 204` (version disabled / `"版本已禁用"`), or `Code: 208` (unrecognized product/channel).

### Legacy Path (`com.softwinner.update`)
The secondary updater is `com.softwinner.update` (DeviceHive framework):
- Endpoints: `http://api.bigbigcloud.cn/dh/v2/rest` and `ws://ws.bigbigcloud.cn/dh/v2/websocket`.
- Status: Servers are unresponsive / timing out; confirmed to be legacy scaffolding retained in stock firmware.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
