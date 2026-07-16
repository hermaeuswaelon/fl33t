# Azazel Browser-Based Social Media Automation

## Overview

Use **Bromium** (the CEF4Delphi browser, socket at `/tmp/aethelgard_cef.sock`) as a real Chromium process to automate social media platforms. Bromium appears as a genuine browser — AI-blocking sites, bot-detection scripts, and login gateways see a real Chromium 131 with extensions, cookies, and a consistent profile.

**Bridge script:** `/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/work/bromium_bridge.py`

## Platform Targets & Methods

### Reddit — Posting, Searching, Profile Research

```bash
# Navigate to Reddit
python3 bromium_bridge.py navigate https://www.reddit.com

# Search for target profiles or topics
python3 bromium_bridge.py navigate "https://www.reddit.com/r/artificial/search/?q=sovereign+AI"

# Research specific user profiles
python3 bromium_bridge.py navigate "https://www.reddit.com/user/SomeTargetUser"

# Make a post (requires logged-in session)
# 1. Navigate to subreddit
# 2. Click "Create Post" button via CDP or coordinate click
# 3. Fill title/body via JS injection
# 4. Submit
```

**Profile cookies persist** in `/tmp/bromium-profile/Default/Cookies`. Log in once, and sessions persist across browser restarts.

**For Lilith Beaux targeting:** Search for profiles that engage with spirituality, yoga, dance, sovereignty, or alt-fashion communities:
```bash
python3 bromium_bridge.py browse reddit
# Then search for "lilith", "yoga", "sovereign feminine", etc.
```

### Craigslist — Scraping Listings & Auto-Applying

```bash
# Navigate to your city's gigs
python3 bromium_bridge.py navigate "https://yourcity.craigslist.org/d/gigs/search/ggg"

# Extract all gig listings via JS
python3 bromium_bridge.py js "
  Array.from(document.querySelectorAll('.result-row')).map(row => ({
    title: row.querySelector('.result-title')?.textContent?.trim(),
    url: row.querySelector('.result-title')?.href,
    date: row.querySelector('.result-date')?.textContent?.trim(),
    price: row.querySelector('.result-price')?.textContent?.trim(),
    location: row.querySelector('.result-hood')?.textContent?.trim()
  }))
"

# Read a specific gig listing
python3 bromium_bridge.py navigate "https://yourcity.craigslist.org/.../1234567890.html"
python3 bromium_bridge.py text  # Get page body text
```

**For bulk scraping multiple cities/categories:**
```python
# From Python / execute_code
from hermes_tools import terminal

cities = ["sfbay", "losangeles", "newyork", "chicago", "austin"]
categories = ["ggg", "wrk", "web"]  # gigs, writing, web dev

for city in cities:
    for cat in categories:
        result = terminal(f"python3 bromium_bridge.py navigate 'https://{city}.craigslist.org/d/{cat}/search/{cat}'")
        # Extract listings, save to file
```

**For auto-applying** (gigs that match your skills): Navigate to the gig page, click "reply" via CDP coordinate, fill the form with a cover letter, and submit. Save your cover letter template and reply email in the profile.

### LinkedIn — Profile Research & Job Search

```bash
# Search for specific profiles
python3 bromium_bridge.py navigate "https://www.linkedin.com/search/results/people/?keywords=Lilith+Beaux"

# Search for jobs
python3 bromium_bridge.py navigate "https://www.linkedin.com/jobs/search/?keywords=freelance&location=remote"

# Read a job posting (use Instant Data Scraper extension for structured extraction)
python3 bromium_bridge.py js "
  // Extract job details
  const job = {};
  job.title = document.querySelector('.job-title')?.textContent?.trim();
  job.company = document.querySelector('.job-company')?.textContent?.trim();
  job.description = document.querySelector('.job-description')?.textContent?.trim();
  JSON.stringify(job);
"
```

**Note:** LinkedIn has aggressive bot detection. Use the Spoof Geolocation extension (`ihdobppgelceaoeojmhpmbnaljhhmhlc`) to match your target location. Log in manually once, then sessions persist.

### Freepascal.com — Scraping Reference

```bash
# Navigate to the Freepascal documentation
python3 bromium_bridge.py navigate "https://www.freepascal.org/docs.html"
python3 bromium_bridge.py text
```

This is useful for Pascal Fleet development — grab function signatures, class references, or compiler documentation.

### Instagram / Facebook — Content Research

```bash
# Facebook profile search (for Lilith Beaux targeting)
python3 bromium_bridge.js "
  // Extract visible profile info
  const info = {};
  info.name = document.querySelector('h1')?.textContent?.trim();
  info.bio = document.querySelector('[data-testid=\"bio\"]')?.textContent?.trim();
  info.friends = document.querySelectorAll('[data-testid=\"friend_count\"]')?.[0]?.textContent?.trim();
  JSON.stringify(info);
"
```

Facebook requires login. Keep a logged-in profile session in `/tmp/bromium-profile/`.

## Bulk Scraping Strategy

For high-volume scraping (e.g., "scrape NUMEROUS Craigslist gigs"), use a batch pattern:

```python
from hermes_tools import write_file, terminal
import json, time, random

results = []
urls = [
    "https://sfbay.craigslist.org/d/gigs/search/ggg",
    "https://losangeles.craigslist.org/d/gigs/search/ggg",
    # ... generate from city list
]

for url in urls:
    r = terminal(f"python3 bromium_bridge.py navigate '{url}'")
    extract = terminal(f"""python3 bromium_bridge.py js "
      JSON.stringify(Array.from(document.querySelectorAll('.result-row')).map(r => ({{
        title: r.querySelector('.result-title')?.textContent?.trim(),
        url: r.querySelector('.result-title')?.href,
        price: r.querySelector('.result-price')?.textContent?.trim()
      }})))
    " """)
    try:
        results.extend(json.loads(extract))
    except:
        pass
    time.sleep(random.uniform(2, 5))  # Rate limit avoidance

write_file("~/Desktop/scraped_gigs.json", json.dumps(results, indent=2))
```

## Pitfalls

- **Sessions expire** — log in again after profile wipe (`rm -rf /tmp/bromium-profile/`)
- **Rate limits** — Craigslist and LinkedIn will throttle rapid requests. Use irrational timers (random × φ/π) between navigations
- **CDP not responding** — Check with `ss -tlnp | grep 9224`. If dead, the browser may need restart
- **JS extraction fragility** — DOM selectors change when sites update. Always verify extracted output
- **LinkedIn bot detection** — Use the Spoof Geolocation extension and keep a warm profile (at least 5 minutes of human-like browsing before scraping)
- **Reddit API > browser** — For high-volume Reddit work, use their API (PRAW) instead of browser automation. Browser is for logged-in interactive tasks like posting

## Related Skills

- `ares-browser-research` — Full Bromium bridge reference (socket protocol, extensions, CDP)
- `bromium-extension-bridge` — Extension control via Unix socket IPC
- `ares-pascal-fleet` — Pascal source compilation and debugging
