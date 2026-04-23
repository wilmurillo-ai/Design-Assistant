# CarsXE API Reference

Base URL: `https://api.carsxe.com`
Auth: append `?key=YOUR_API_KEY` to every request.  
Docs: https://api.carsxe.com/docs

---

## Table of Contents

1. [Vehicle Specs (VIN Decode)](#1-vehicle-specs-vin-decode)
2. [License Plate Decoder](#2-license-plate-decoder)
3. [Market Value](#3-market-value)
4. [Vehicle History](#4-vehicle-history)
5. [Vehicle Images](#5-vehicle-images)
6. [Safety Recalls](#6-safety-recalls)
7. [Lien & Theft](#7-lien--theft)
8. [International VIN Decoder](#8-international-vin-decoder)
9. [Year/Make/Model (YMM)](#9-yearmakemodel-ymm)
10. [OBD Code Decoder](#10-obd-code-decoder)
11. [VIN OCR](#11-vin-ocr)
12. [Plate Image Recognition](#12-plate-image-recognition)

---

## 1. Vehicle Specs (VIN Decode)

**Endpoint:** `GET /specs`

**Parameters:**

| Param | Required | Description         |
| ----- | -------- | ------------------- |
| `key` | Yes      | Your CarsXE API key |
| `vin` | Yes      | 17-character VIN    |

**Response fields (key ones):**

- `input.vin` — validated VIN
- `attributes.year`, `attributes.make`, `attributes.model`, `attributes.trim`
- `attributes.engine` — displacement, cylinders, fuel type, horsepower, torque
- `attributes.transmission` — type, speeds
- `attributes.drivetrain` — AWD/FWD/RWD/4WD
- `attributes.doors`, `attributes.body_type`
- `attributes.dimensions` — wheelbase, length, width, height, weight
- `attributes.fuel` — tank capacity, city/hwy MPG
- `attributes.colors` — interior/exterior options
- `attributes.equipment` — standard and optional features list

**Example:**

```
GET /specs?key=KEY&vin=WBAFR7C57CC811956
```

---

## 2. License Plate Decoder

**Endpoint:** `GET /platedecoder`

**Parameters:**

| Param     | Required | Description                                                                      |
| --------- | -------- | -------------------------------------------------------------------------------- |
| `key`     | Yes      | Your CarsXE API key                                                              |
| `plate`   | Yes      | License plate number                                                             |
| `country` | Yes      | Country code (e.g., `US`, `CA`, `GB`)                                            |
| `state`   | No       | State/province abbreviation (e.g., `CA`, `NY`) — improves accuracy for US plates |

**Response fields:**

- `vin` — resolved VIN
- `make`, `model`, `year`
- `state`, `country`
- Basic vehicle attributes

**Tip:** After decoding a plate, chain to `/specs`, `/history`, or `/recalls` using the returned VIN.

**Example:**

```
GET /platedecoder?key=KEY&plate=7XER187&state=CA&country=US
```

---

## 3. Market Value

**Endpoint:** `GET /marketvalue`

**Parameters:**

| Param     | Required | Description                                      |
| --------- | -------- | ------------------------------------------------ |
| `key`     | Yes      | Your CarsXE API key                              |
| `vin`     | Yes      | 17-character VIN                                 |
| `state`   | No       | US state abbreviation (affects regional pricing) |
| `country` | No       | Country code                                     |

**Response fields:**

- `retail` — estimated retail price
- `trade_in` — trade-in value
- `msrp` — original MSRP
- `mileage_adjustment` — adjustment based on recorded mileage
- `condition` — assumed condition
- `currency` — USD by default

**Example:**

```
GET /marketvalue?key=KEY&vin=WBAFR7C57CC811956
```

---

## 4. Vehicle History

**Endpoint:** `GET /history`

**Parameters:**

| Param    | Required | Description               |
| -------- | -------- | ------------------------- |
| `key`    | Yes      | Your CarsXE API key       |
| `vin`    | Yes      | 17-character VIN          |
| `format` | No       | `json` (default) or `xml` |

**Response fields:**

- `junk` — junk/salvage title records
- `insurance` — insurance loss records
- `brands` — title brands (rebuilt, flood, fire, etc.)
- `titles` — title history by state
- `odometer` — odometer readings over time
- `theft` — theft/recovery records
- `accidents` — accident/damage records (where available)
- `exports` — export records

**Example:**

```
GET /history?key=KEY&vin=WBAFR7C57CC811956
```

---

## 5. Vehicle Images

**Endpoint:** `GET /images`

**Parameters:**

| Param         | Required | Description                         |
| ------------- | -------- | ----------------------------------- |
| `key`         | Yes      | Your CarsXE API key                 |
| `make`        | Yes      | Vehicle make (e.g., `BMW`)          |
| `model`       | Yes      | Vehicle model (e.g., `X5`)          |
| `year`        | No       | Year (e.g., `2019`)                 |
| `trim`        | No       | Trim level                          |
| `color`       | No       | Color name (e.g., `blue`, `white`)  |
| `transparent` | No       | `true` for transparent background   |
| `angle`       | No       | `front`, `rear`, `side`, `interior` |
| `photoType`   | No       | `studio`, `lifestyle`               |
| `size`        | No       | `small`, `medium`, `large`          |
| `license`     | No       | License type filter                 |
| `format`      | No       | `json` (default)                    |

**Response fields:**

- Array of image objects with `url`, `width`, `height`, `color`, `angle`, `year`

**Example:**

```
GET /images?key=KEY&make=BMW&model=X5&year=2019&color=blue
```

---

## 6. Safety Recalls

**Endpoint:** `GET /recalls`

**Parameters:**

| Param | Required | Description         |
| ----- | -------- | ------------------- |
| `key` | Yes      | Your CarsXE API key |
| `vin` | Yes      | 17-character VIN    |

**Response fields:**

- `total` — number of recalls found
- `recalls[]` — array of recall objects:
  - `date` — recall date
  - `description` — what's being recalled
  - `risk` — safety risk description
  - `remedy` — fix/remedy description
  - `status` — open/closed
  - `nhtsa_id` — NHTSA campaign number

**Important:** Always highlight open recalls prominently for the user.

**Example:**

```
GET /recalls?key=KEY&vin=1C4JJXR64PW696340
```

---

## 7. Lien & Theft

**Endpoint:** `GET /lientheft`

**Parameters:**

| Param | Required | Description         |
| ----- | -------- | ------------------- |
| `key` | Yes      | Your CarsXE API key |
| `vin` | Yes      | 17-character VIN    |

**Response fields:**

- `lien` — lien records (active loans/encumbrances)
- `theft` — theft/stolen vehicle records
- `recovery` — recovery records if stolen

**Important:** Flag any active liens or unresolved theft records prominently — these are critical for buyers.

**Example:**

```
GET /lientheft?key=KEY&vin=WBAFR7C57CC811956
```

---

## 8. International VIN Decoder

**Endpoint:** `GET /internationalvin`

**Parameters:**

| Param | Required | Description                        |
| ----- | -------- | ---------------------------------- |
| `key` | Yes      | Your CarsXE API key                |
| `vin` | Yes      | 17-character VIN (non-US vehicles) |

**Response fields:** Similar to `/specs` but includes international-specific fields:

- `manufacturer_country`
- `emissions_standard` — Euro NCAP ratings where applicable
- `regional_specs`

Use this endpoint for VINs that don't start with 1, 2, 3, 4, or 5 (those are North American).

**Example:**

```
GET /internationalvin?key=KEY&vin=WF0MXXGBWM8R43240
```

---

## 9. Year/Make/Model (YMM)

**Endpoint:** `GET /ymm`

**Parameters:**

| Param   | Required | Description                    |
| ------- | -------- | ------------------------------ |
| `key`   | Yes      | Your CarsXE API key            |
| `year`  | Yes      | Model year (e.g., `2020`)      |
| `make`  | Yes      | Make (e.g., `Toyota`)          |
| `model` | Yes      | Model (e.g., `Camry`)          |
| `trim`  | No       | Trim level (e.g., `LE`, `XSE`) |

**Response fields:**

- Vehicle specs similar to `/specs`
- `colors` — available colors for that year/trim
- `features` — standard features list
- `options` — available option packages
- `configurations` — all available trims if no trim specified

Use when the user doesn't have a VIN but knows the year, make, and model.

**Example:**

```
GET /ymm?key=KEY&year=2020&make=Toyota&model=Camry&trim=LE
```

---

## 10. OBD Code Decoder

**Endpoint:** `GET /obd`

**Parameters:**

| Param  | Required | Description                                            |
| ------ | -------- | ------------------------------------------------------ |
| `key`  | Yes      | Your CarsXE API key                                    |
| `code` | Yes      | OBD-II code (e.g., `P0300`, `C0035`, `B1234`, `U0100`) |

**Code prefixes:**

- `P` — Powertrain (engine, transmission)
- `C` — Chassis (brakes, suspension)
- `B` — Body (airbags, comfort systems)
- `U` — Network/Communication

**Response fields:**

- `code` — the code
- `description` — plain-language description of the fault
- `diagnosis` — likely causes
- `date` — when the code was last updated in the database

**Example:**

```
GET /obd?key=KEY&code=P0300
```

---

## 11. VIN OCR

**Endpoint:** `POST /vinocr`

**Method:** POST  
**Content-Type:** `application/json`

**Request body:**

```json
{
  "imageUrl": "https://example.com/vin-sticker.jpg"
}
```

**Query params:** `?key=YOUR_API_KEY`

**Response fields:**

- `vin` — detected VIN string
- `confidence` — confidence score (0–1)
- `bounding_box` — pixel coordinates of VIN in image
- `candidates` — alternative VIN readings if confidence is low

Use for images of VIN stickers, door jambs, or dashboard VIN plates.

**Example:**

```
POST /vinocr?key=KEY
Body: {"imageUrl":"https://res.cloudinary.com/carsxe/image/upload/q_auto/f_auto/v1713204144/base/images/vin-ocr/vin.jpg"}
```

---

## 12. Plate Image Recognition

**Endpoint:** `POST /platerecognition`

**Method:** POST  
**Content-Type:** `application/json`

**Request body:**

```json
{
  "imageUrl": "https://example.com/car-photo.jpg"
}
```

**Query params:** `?key=YOUR_API_KEY`

**Response fields:**

- `plates[]` — array of detected plates:
  - `plate` — plate text
  - `confidence` — confidence score
  - `bounding_box` — pixel coordinates in image
  - `vehicle_type` — car, truck, motorcycle, etc.
  - `country` / `state` — inferred location (where detectable)

Use for photos of vehicles where you want to extract the plate number.

**Example:**

```
POST /platerecognition?key=KEY
Body: {"imageUrl":"https://api.carsxe.com/img/apis/plate_recognition.JPG"}
```

---

## VIN Region Guide

| First character | Region         |
| --------------- | -------------- |
| 1, 4, 5         | United States  |
| 2               | Canada         |
| 3               | Mexico         |
| J               | Japan          |
| W               | Germany        |
| S               | United Kingdom |
| V               | France/Spain   |
| Z               | Italy          |
| K               | Korea          |

Use `/internationalvin` for non-North American VINs (not starting with 1–5).
