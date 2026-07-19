---
name: workspace
description: "Workspace productivity tools — Google Workspace (Gmail, Calendar, Drive, Docs, Sheets), Notion, Airtable, Maps/geolocation"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [productivity, workspace, google, notion, airtable, maps, gmail, calendar, drive]
    related_skills: [himalaya, nano-pdf, ocr-and-documents, powerpoint]
---

# Workspace Umbrella

Consolidated skill for workspace productivity tools. Absorbs: google-workspace, notion, airtable, maps.

## Contents

1. [Google Workspace](#1-google-workspace)
2. [Notion](#2-notion)
3. [Airtable](#3-airtable)
4. [Maps & Geolocation](#4-maps--geolocation)

---

## 1. Google Workspace

Gmail, Calendar, Drive, Contacts, Sheets, and Docs via Hermes-managed OAuth.

### Setup

Run one-time OAuth setup:
```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --check  # Check if authenticated
# Follow interactive OAuth flow if not
```

### Gmail

```bash
GAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI gmail search "is:unread" --max 10
$GAPI gmail get MESSAGE_ID
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"
$GAPI gmail reply MESSAGE_ID --body "Thanks"
```

### Calendar

```bash
$GAPI calendar list
$GAPI calendar create --summary "Meeting" --start 2026-03-01T10:00:00Z --end 2026-03-01T11:00:00Z
```

### Drive

```bash
$GAPI drive search "project report"
$GAPI drive upload /path/to/file.pdf
$GAPI drive download FILE_ID
$GAPI drive share FILE_ID --email user@example.com --role reader
```

### Sheets & Docs

```bash
$GAPI sheets create --title "Budget" --sheet-name "Q1"
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[[...]]'
$GAPI docs create --title "Meeting Notes" --body "Content..."
$GAPI docs append DOC_ID --text "Additional content"
```

### Rules

- Never send email, create/delete events, delete/share files without user confirmation
- Calendar times must include timezone (ISO 8601 with offset)
- Check auth with `setup.py --check` before first use

---

## 2. Notion

Notion API via `ntn` CLI (preferred, macOS/Linux) or HTTP + curl fallback.

### Setup

```bash
# Get integration token from notion.so/my-integrations
export NOTION_API_KEY=ntn_your_key_here

# Install ntn (optional, macOS/Linux)
curl -fsSL https://ntn.dev | bash
export NOTION_API_TOKEN=$NOTION_API_KEY
```

### Read/Write Pages

**With ntn:**
```bash
ntn api v1/pages/{page_id}/markdown  # Read as markdown
ntn api v1/pages parent[page_id]=xxx properties[title][0][text][content]="Title" markdown="# Content"
```

**With curl:**
```bash
curl -s "https://api.notion.com/v1/pages/{id}/markdown" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### Query Databases

```bash
ntn api v1/data_sources/{ds_id}/query -X POST filter[property]=Status filter[select][equals]=Active
```

### Notion Workers (Business+)

```bash
ntn workers new my-worker
ntn workers deploy --name my-worker
```

---

## 3. Airtable

Airtable REST API via curl. Personal Access Token required.

### Setup

```bash
export AIRTABLE_API_KEY=pat_your_token
```

### Common Operations

```bash
# List bases
curl -s "https://api.airtable.com/v0/meta/bases" -H "Authorization: Bearer $AIRTABLE_API_KEY"

# List records
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=10" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY"

# Filter (URL-encode the formula)
ENC=$(python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=''))" "{Status}='Todo'")
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?filterByFormula=$ENC" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY"

# Create/Update/Delete records
curl -s -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" -H "Content-Type: application/json" \
  -d '{"fields": {"Name": "New task", "Status": "Todo"}}'

# Upsert by merge field
curl -s -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" -H "Content-Type: application/json" \
  -d '{"performUpsert": {"fieldsToMergeOn": ["Email"]}, "records": [...]}'
```

### Key Notes

- Rate limit: 5 req/sec/base. Batch up to 10 records per request.
- PATCH merges fields; PUT replaces entire record. Use PATCH.
- URLs need `%5B`/`%5D` for square brackets
- Default to `python3 -m json.tool` for pretty-printing
- Always inspect schema before mutating with `GET /meta/bases/$ID/tables`

---

## 4. Maps & Geolocation

Geocode, find nearby places, routing, and timezone data via OpenStreetMap/Nominatim/OSRM.

### Setup

No API key needed. Script at `~/.hermes/skills/maps/scripts/maps_client.py`:
```bash
MAPS=~/.hermes/skills/maps/scripts/maps_client.py
```

### Commands

**Geocode:** `python3 $MAPS search "Eiffel Tower"`
**Reverse geocode:** `python3 $MAPS reverse 48.8584 2.2945`
**Nearby POIs:** `python3 $MAPS nearby 48.8584 2.2945 restaurant --limit 10`
**By address:** `python3 $MAPS nearby --near "Times Square, New York" --category cafe`
**Distance:** `python3 $MAPS distance "Paris" --to "Lyon" --mode driving`
**Directions:** `python3 $MAPS directions "Eiffel Tower" --to "Louvre" --mode walking`
**Timezone:** `python3 $MAPS timezone 48.8584 2.2945`
**Area/bbox:** `python3 $MAPS area "Manhattan"` then `bbox S W N E category`

### 46 POI Categories

restaurant, cafe, bar, hospital, pharmacy, hotel, supermarket, atm, gas_station, parking, museum, park, school, university, bank, police, fire_station, library, airport, train_station, bus_stop, church, mosque, synagogue, dentist, doctor, cinema, theatre, gym, swimming_pool, post_office, convenience_store, bakery, bookshop, laundry, car_wash, car_rental, bicycle_rental, taxi, veterinary, zoo, playground, stadium, nightclub, camp_site, guest_house.

### Pitfalls

- Nominatim max 1 req/s (automatic)
- OSRM best in Europe/North America
- Works great with Telegram location pins
