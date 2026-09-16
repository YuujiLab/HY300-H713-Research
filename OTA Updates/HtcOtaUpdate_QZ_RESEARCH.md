# HtcOtaUpdate_QZ OTA Update Research

## 1. Overview
The `HtcOtaUpdate_QZ` application is the active component responsible for online update checks on the HY300 Pro. It communicates with a custom API hosted at `triplesai.com`.

## 2. API Details
- **Base URL:** `http://ota.triplesai.com:8080`
- **Endpoints:**
  - `POST /V1/Ota/Check`: Main version check.
  - `POST /V1/Ota/CheckDevice`: Device verification (likely for activation/whitelist).

## 3. Communication Protocol

### Headers
Every request includes:
- `AppID`: `1`
- `Timestamp`: Current Unix timestamp in milliseconds (e.g., `1772378114311`).
- `Sign`: SHA1 signature of the JSON body fields.
- `Content-Type`: `application/json; charset=utf-8`

### Signature Algorithm
The `Sign` header is generated as follows:
1. Take all fields from the JSON body.
2. Sort the keys alphabetically.
3. Concatenate key and value pairs into a single string (e.g., `Key1Value1Key2Value2`).
4. Skip fields with empty values or nulls.
5. Generate a SHA1 hash of the resulting string in lowercase.

**Example String for `Check`:**
`ChannelHY200Pro_en_MagcubicOS_public_EMMC_cyhIMEIHYTY62508092801MAC7C:28:64:4A:A8:3DModelaodinVersionprojector.20250721.172901`

### Registration/Check Body Fields
Used in `/V1/Ota/Check`:
- `Version`: Current OTA version string (e.g., `projector.20250721.172901`).
- `Channel`: `HY200Pro_en_MagcubicOS_public_EMMC_cyh`.
- `Model`: `aodin`.
- `IMEI`: Hardware Serial Number (e.g., `HYTY62508092801`).
- `MAC`: WiFi MAC address with colons (e.g., `7C:28:64:4A:A8:3D`).

Used in `/V1/Ota/CheckDevice`:
- `ExpNum`: Hardware Serial Number.

## 4. Response Codes & Server Behaviors
- **`Code: 0`:** Success / Device Verified / Update Available.
- **`Code: 204`:** Version Disabled (`"版本已禁用"`). The server recognizes the Model, Channel, and Hardware ID, but the specific firmware build has been marked as disabled/deprecated on the vendor backend.
- **`Code: 208`:** Product does not exist. Returned when the Model/Channel/Version combination is completely unregistered in the database (e.g., legacy test strings like `projector.20250721.172901`).

### Verified Probe Example (`Code: 204`)
Probing the production build version string (`projector.20250922.093247`):

```bash
curl -H 'AppID: 1' \
     -H 'Content-Type: application/json; charset=utf-8' \
     -H 'Host: ota.triplesai.com:8080' \
     -H 'Connection: Keep-Alive' \
     --compressed \
     -H 'User-Agent: okhttp/3.4.1' \
     -X POST http://ota.triplesai.com:8080/V1/Ota/Check \
     -d '{"Version":"projector.20250922.093247","Channel":"HY200Pro_en_MagcubicOS_public_EMMC_cyh","Model":"aodin","IMEI":"HYTY62508092801","MAC":"7C:28:64:4A:A8:3D"}'
```

**Server Response:**
```json
{
  "Code": 204,
  "Message": "版本已禁用",
  "Data": null
}
```

## 5. Summary Findings
- The signature verification algorithm requires lowercased SHA1 hashing of alphabetically sorted JSON keys.
- The `ota.triplesai.com` server is actively online and maintaining device definitions for model `aodin` on channel `HY200Pro_en_MagcubicOS_public_EMMC_cyh`.
- The production build `projector.20250922.093247` is explicitly marked as disabled (`Code 204`), indicating vendor deprecation or freeze of automated updates for this revision.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
