# Cliento API & Booking Flow Reference

This document contains the strict `curl` commands, URLs, and JSON structures required to execute Cliento operations.

## Critical Security & Sanitization Rules
When executing any of the bash `curl` commands below, you MUST sanitize all variables before interpolating them into your command string:
1. **No Shell Injection:** Ensure variables like `company_id`, `URL`, `first_name`, `email`, or `note` do not contain unescaped single quotes (`'`) or double quotes (`"`). Reject any input that contains bash control characters (`;`, `&&`, `$()`, `` ` ``).
2. **JSON Integrity:** When building the `POST` data payload, dynamically escape any quotation marks in user fields (like the `note` field) so the JSON is not corrupted.
3. **URL Validation:** Any public Cliento URL must strictly start with `https://cliento.com/` and contain no spaces.

---

## Action 1: Registering a Store
**Command to fetch metadata:**
```bash
curl -s "<URL>"
```
**Parsing:** Extract the JSON payload located inside the `<script id="__NEXT_DATA__" type="application/json">` tag.
- **Company ID:** `props.pageProps.business.stableId`
- **Services:** Array at `props.pageProps.refData.services` (`id`, `name`, `price`)
- **Barbers:** Array at `props.pageProps.refData.resources` (`id`, `name`)

---

## Action 2 & 3: Checking Availability
**Construct URL:**
`https://web.prod.cliento.com/api/v2/partner/cliento/{company_id}/resources/slots?fromDate={YYYY-MM-DD}&srvIds={service_id}&toDate={YYYY-MM-DD}`
*(Optional: append `&resIds={resource_id}` if applicable)*

**Command:**
```bash
curl -s "<CONSTRUCTED_URL>"
```
**Parsing:** Extract the `date` and `time` fields from `resourceSlots[0].slots`. Include `resourceSlots[0].hashId` for future steps.

---

## Action 4: Reserving a Slot
Reserves a time slot temporarily for ~5 minutes. Requires `slotKey` (from the availability check's `key` field).

**Command:**
```bash
curl -s -X POST "https://web.prod.cliento.com/api/v2/partner/cliento/{company_id}/booking/reserve" \
  -H "Content-Type: application/json" \
  -d '{"slotKey": "{slot_key}"}'
```
**Parsing:** Store the returned `cbUuid`. Present the `reservationExpiry`, `services`, and `price` to the user.

---

## Action 6: Confirming a Booking

### Step 1: Check Custom Fields
```bash
curl -s -X GET "https://cliento.com/api/v2/partner/cliento/{company_id}/custom-fields/resource/{resourceHashId}?srvIds={service_id}"
```

### Step 2: Submit Customer Details
Substitute the sanitized user preferences into the payload.
```bash
curl -s -X POST "https://cliento.com/api/v2/partner/cliento/{company_id}/booking/customer" \
  -H "Content-Type: application/json" \
  -d '{
    "cbUuid": "{cb_uuid_from_reserve_step}",
    "name": "{first_name} {last_name}",
    "email": "{email}",
    "phone": "{phone_number}",
    "note": "{optional_note_escaped}",
    "customFields": null,
    "allowMarketing": null,
    "bookedSpecificResource": {true_or_false},
    "attributes": null
  }'
```

### Step 3: Get Confirmation Options
```bash
curl -s -X POST "https://cliento.com/api/v2/partner/cliento/{company_id}/booking/confirmation-options" \
  -H "Content-Type: application/json" \
  -d '{"cbUuid": "{cb_uuid_from_reserve_step}"}'
```
*Wait: Verify `"confirmationMethod": "NoPin"` in response. If a real pin is needed, halt and ask the user.*

### Step 4: Confirm Booking
```bash
curl -s -X POST "https://cliento.com/api/v2/partner/cliento/{company_id}/booking/confirm" \
  -H "Content-Type: application/json" \
  -d '{
    "cbUuid": "{cb_uuid_from_reserve_step}",
    "pin": "{pin_value_based_on_options}"
  }'
```
*A successful response includes `"emailConfirmSent": true`.*