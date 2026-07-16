# Ephemeris-Based Web Tool — Implementation Blueprint

## Pattern: Browser-Side Ephemeris + Map Overlay + GitHub Pages

This reference documents how to build a deployable web tool that:
1. Computes real-time planetary transit positions entirely in-browser
2. Projects astrological geometry (Merkaba, hexagram) onto a Leaflet map
3. Detects active transits aspects against a fixed composite chart
4. Deploys as a zero-cost static site on GitHub Pages

## Technology Stack

| Layer | Library | Source | Why |
|-------|---------|--------|-----|
| **Ephemeris** | [astronomy-engine](https://github.com/cosinekitty/astronomy) | CDN: `https://cdn.jsdelivr.net/npm/astronomy-engine/astronomy.browser.min.js` | Pure JS, no deps, Pluto support, MIT license |
| **Maps** | [Leaflet 1.9.4](https://leafletjs.com/) | CDN: `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js` | Lightweight, dark tile support, no API key |
| **Dark tiles** | CartoDB dark | `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png` | Free, no API key, aesthetic match |
| **Hosting** | GitHub Pages | Repo → Settings → Pages | Free static hosting, custom domain optional |

## Browser Ephemeris Setup

```html
<script src="https://cdn.jsdelivr.net/npm/astronomy-engine/astronomy.browser.min.js"></script>
<script>
// Get ecliptic longitude for any planet at any date
const pos = Astronomy.EclipticLongitude(Astronomy.Body.Saturn, new Date());
// Returns degrees in ecliptic longitude of date

// Available bodies:
const BODIES = {
  Sun: Astronomy.Body.Sun,
  Moon: Astronomy.Body.Moon,
  Mercury: Astronomy.Body.Mercury,
  Venus: Astronomy.Body.Venus,
  Mars: Astronomy.Body.Mars,
  Jupiter: Astronomy.Body.Jupiter,
  Saturn: Astronomy.Body.Saturn,
  Uranus: Astronomy.Body.Uranus,
  Neptune: Astronomy.Body.Neptune,
  Pluto: Astronomy.Body.Pluto
};

// Convert ecliptic longitude to zodiac notation
function zodiacStr(deg) {
  deg = ((deg % 360) + 360) % 360;
  const SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio',
                 'Sagittarius','Capricorn','Aquarius','Pisces'];
  const s = Math.floor(deg / 30);
  const d = deg - s * 30;
  return `${SIGNS[s]} ${d.toFixed(1)}°`;
}
</script>
```

## Transit Detection Algorithm

```
For each composite chart point (sun, moon, merc, ven, mars, jup, sat, uran, nept, plu):
  For each transiting planet:
    Compute angular difference
    Check against aspect orbs:
      Conjunction: 0° ± 8°
      Opposition:  180° ± 8°
      Trine:       120° ± 8°
      Square:      90° ± 6°
      Sextile:     60° ± 6°
    If within orb → record aspect with strength = 1 - (exact_orb / max_orb)
```

## Merkaba Projection Math

Convert composite chart zodiac positions to compass bearings on the physical grid:

```javascript
function bearingFromZodiac(deg) {
  // Convert zodiac longitude (0° Aries = 0°) to compass bearing
  return ((deg * -1 + 90) % 360 + 360) % 360;
}

function destFromBearing(lat, lng, bearingDeg, distKm) {
  // Haversine — project a point at given bearing + distance from origin
  const R = 6371;
  const brng = bearingDeg * Math.PI / 180;
  const d = distKm / R;
  const φ1 = lat * Math.PI / 180;
  const λ1 = lng * Math.PI / 180;
  const φ2 = Math.asin(Math.sin(φ1)*Math.cos(d) + Math.cos(φ1)*Math.sin(d)*Math.cos(brng));
  const λ2 = λ1 + Math.atan2(
    Math.sin(brng)*Math.sin(d)*Math.cos(φ1),
    Math.cos(d)-Math.sin(φ1)*Math.sin(φ2)
  );
  return { lat: φ2 * 180 / Math.PI, lng: λ2 * 180 / Math.PI };
}
```

## Leaflet Dark Map with Overlays

```javascript
const map = L.map('map', { center: [baseLat, baseLng], zoom: 15 });
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);

// DivIcon markers — custom HTML for glyphic/cosmic aesthetic
const icon = L.divIcon({
  html: `<div style="width:10px;height:10px;background:#ff6644;border-radius:50%;box-shadow:0 0 8px #ff6644"></div>`,
  iconSize: [10,10], iconAnchor: [5,5], className: ''
});

// Polylines for Merkaba edges and rays
L.polyline([[lat1,lng1], [lat2,lng2]], {
  color: '#b8860b', weight: 1, opacity: 0.4, dashArray: '4,6'
}).addTo(map);

// Polygons for camera fan wedges
L.polygon([[center.lat,center.lng], [end1.lat,end1.lng], [end2.lat,end2.lng]], {
  color: '#44ff44', weight: 1, fillColor: '#44ff44', fillOpacity: 0.05
}).addTo(map);
```

## GitHub Pages Deployment

```bash
# One-time setup
git init && git add -A && git commit -m "Initial"
gh repo create <repo-name> --public --source . --push
gh api repos/<user>/<repo>/pages -X POST --input - <<'EOF'
{"source":{"branch":"main","path":"/"}}
EOF

# Site is live at: https://<user>.github.io/<repo>/
```

## Useful astronomy-engine Functions

| Function | Returns | Notes |
|----------|---------|-------|
| `Astronomy.EclipticLongitude(body, date)` | Degrees in ecliptic of date | Primary function for zodiac positions |
| `Astronomy.GeoVector(body, date)` | 3D vector (AU) | Raw heliocentric position |
| `Astronomy.Equator(body, date)` | RA/Dec | Equatorial coordinates |
| `Astronomy.Horizon(date, observer, ra, dec, refraction)` | Az/Alt | Local horizon coordinates |
| `Astronomy.MakeObserver(lat, lon, elevation)` | Observer object | For local calculations |
| `Astronomy.SearchAltitude(body, observer, direction, startDate, limitDays)` | Date | Rise/set times |
| `Astronomy.SearchPlanetApsis(body, startDate)` | Date | Perihelion/aphelion |

## Pitfalls

- **astronomy-engine uses TT (Terrestrial Time)** internally but accepts JS Date (approximated as UTC). For astrological transit work (±1 day resolution) this is fine. For precise degree-level accuracy (house cusps, exact aspects), account for TT-UTC offset (~69s currently).
- **Pluto** is supported but with lower precision than the major planets (it's a numerical integration, not analytic). Degrees are reliable to ~0.1°.
- **Moon** position is very accurate but changes rapidly — compute per-minute for precise lunar aspects.
- **Leaflet tiles** — ensure the dark tile URL is correct. CartoDB changed their URL scheme in 2023. The current valid URL is `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`.
- **GitHub Pages** first deployment takes 1-2 minutes. First visit may return 404 if the build hasn't completed.
- **Single HTML file** is preferred for Pages deployment to avoid CORS issues with relative paths.
