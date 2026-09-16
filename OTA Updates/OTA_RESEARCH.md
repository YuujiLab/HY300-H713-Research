# HY300 Pro OTA Update Research

## 1. Overview
The HY300 Pro projector uses a custom OTA update system provided by `bigbigcloud.cn` (Softwinner/Allwinner ecosystem). The update process is handled by `com.softwinner.update` which acts as a client for the DeviceHive-based API.

## 2. API Details
- **Base URL:** `http://api.bigbigcloud.cn/dh/v2/rest`
- **WebSocket URL:** `ws://ws.bigbigcloud.cn/dh/v2/websocket`
- **License Key:** `1a2fafe7456caca93ab41e3eea0de13076ff0af5ae83605a084ede7ea3e720365d6bc62bfd984fbd`

## 3. Communication Protocol

### Authentication
Authentication is performed via custom HTTP headers:
- `Auth-Timestamp`: Current Unix timestamp (seconds).
- `Auth-Signature`: SHA1 hash of a concatenated string.

### Registration (`PUT /device`)
Used to register the device and obtain a `deviceGuid`.
- **Endpoint:** `PUT /device`
- **Signature String:** `deviceId + mac + vendor + deviceClassName + timestamp + license`
- **Payload Fields:**
  - `deviceId`: Hardware Serial Number.
  - `mac`: WiFi MAC address (uppercase, no colons).
  - `vendor`: Device Brand (e.g., ADT-3).
  - `deviceClass`: Object with `name` (e.g., adt3).
  - `firmwareVersion`: Current OTA version string.

### Update Check (`POST /otaupdate`)
Checks for available firmware updates.
- **Endpoint:** `POST /device/{deviceGuid}/otaupdate`
- **Signature String:** `deviceGuid + timestamp + license`
- **Payload Fields:**
  - `deviceGuid`: Obtained from registration.
  - `curVersion`: Current OTA version.
  - `vendor`: Brand.
  - `romType`: "STABLE".
  - `mac`: MAC address.
  - `deviceId`: Serial Number.

## 4. Update Response Structure
A successful update check returns a JSON response with:
- `packUrl`: Direct download link for the update package.
- `packMD5`: MD5 hash for verification.
- `newVersion`: Version string of the available update.
- `packSize`: Size in bytes.

## 5. Summary Findings
The `api.bigbigcloud.cn` server appears to be unresponsive or restricted during testing (Timeouts). Given that `HtcOtaUpdate_QZ` is the active app performing checks, this DeviceHive-based system may be a legacy component or a secondary fallback that is currently inactive for this model.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
