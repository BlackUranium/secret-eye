# JS Secret & API Endpoint Finder

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Automated tool that crawls a target website's public JavaScript files and hunts for **leaked secrets, API keys, tokens, and hidden internal endpoints**.

Frontend bundles often ship production credentials straight to the browser. This tool detects those leaks using a curated set of regex patterns and reports them per JS file — useful for bug bounty, pentesting, and defensive audits.

Looking for an easy way to **find API keys, auth tokens, and hardcoded credentials left behind in public JavaScript bundles**? Whether you are running bug bounty recon, penetration testing, or a defensive code audit of your own SaaS, `secret-eye` does the heavy lifting automatically — from one URL or a whole list of targets — and saves results you can hand off as a readable `.txt` or JSON report.

## How It Works

1. **Discover** — the tool fetches the target page and collects every referenced `.js` file (`modules/scraper.py`).
2. **Scan** — each JS file is downloaded and checked against a curated regex library in `patterns.py` (`modules/scanner.py`).
3. **Report** — findings are grouped by pattern category, printed to the console, and optionally saved to a `.txt` or `.json` report.

## Features

- **Crawls every `.js` file** referenced by a target page (handles relative and absolute paths)
- **Detects 20+ patterns**: Google & AWS keys, GitHub/GitLab tokens, JWT, Stripe, Slack, Telegram bot tokens, private keys, Firebase URLs, hidden `/api/...` endpoints, and more
- **Concurrent scanning** with configurable thread count (`-t`)
- **Scan a single URL or a whole list** of targets (`-l`)
- **Save readable `.txt` or structured `.json` reports** (`-o`, `--json`)
- **Colorized console output** with per-file and per-category findings

## Requirements

- Python 3.8+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Scan a single target

```bash
python main.py -u https://example.com
```

### Scan multiple targets from a list

Create `targets.txt` (lines starting with `#` are ignored):

```
# my targets
https://example.com
https://example.org
```

```bash
python main.py -l targets.txt -t 15
```

### Save a report

```bash
# readable text report
python main.py -u https://example.com -o report.txt

# JSON report (auto-detected by extension, or forced with --json)
python main.py -u https://example.com -o report.json
python main.py -u https://example.com --json -o report.txt
```

### Options

| Flag                | Description                                   |
|---------------------|-----------------------------------------------|
| `-u, --url`         | Target URL to scan (e.g., `https://example.com`) |
| `-l, --list`        | File with one target URL per line             |
| `-o, --output`      | Save the report to a file                     |
| `--json`            | Force JSON report format                      |
| `-t, --threads`     | Number of concurrent scan threads (default: 10) |

Exactly one of `-u` or `-l` is required.

## Use Cases

- **Bug bounty recon** — scan your target list before writing up findings; leaked keys often expand your attack surface.
- **Penetration testing** — find hardcoded credentials and internal `/api/` endpoints that reveal backend structure.
- **SaaS security audits** — verify your own frontend bundles don't leak production `sk_live_` keys, JWTs, or Firebase URLs.
- **OSINT & exposure checks** — map which secrets are discoverable from any publicly reachable page.

## Detected Patterns

| Category                    | Example                                   |
|-----------------------------|-------------------------------------------|
| Google API Key              | `AIzaSy...`                               |
| AWS Access Key ID           | `AKIA...`                                 |
| Telegram Bot Token          | `123456789:AAF...`                        |
| JSON Web Token (JWT)        | `eyJ...`                                  |
| GitHub Token                | `ghp_...` / `github_pat_...`              |
| GitLab Private Token        | `glpat-...`                               |
| Slack Token                 | `xoxb-...` / `xoxp-...`                   |
| Stripe Secret Key           | `sk_live_...`                             |
| Stripe Publishable Key      | `pk_live_...`                             |
| SendGrid API Key            | `SG.xxx.yyy`                              |
| Twilio API Key              | `SK...`                                   |
| Heroku API Key              | `heroku_...`                              |
| Mailgun API Key             | `key-...`                                 |
| Square Access Token         | `sq0atp-...`                              |
| Private Key                 | `-----BEGIN RSA PRIVATE KEY-----`         |
| Firebase Database URL       | `https://xxx.firebaseio.com`              |
| npm Auth Token              | `//registry.npmjs.org/:_authToken=...`    |
| Generic API Key/Secret      | `api_key = "..."`                         |
| Internal/Hidden Endpoint    | `/api/v1/admin/...`                       |
| URL / Staging Domain        | `https://staging.example.com`             |

## Example Output

```
[*] Fetching JS files from: https://example.com
[+] Found 3 JavaScript file(s).
[*] Analyzing for secret leaks & endpoints...
============================================================

[1/3] Scanning: https://example.com/app.js
   └── [!] Google API Key:
      AIzaSyAbCDef...
   └── [!] Internal/Hidden Endpoint:
      /api/v1/admin/users

[2/3] Scanning: https://example.com/vendor.min.js
   └── [✓] Clean (no secret patterns found)

[!] Scan complete! Total potential secrets detected: 3
```

## FAQ

**Why does it say "No .js files found" even though the site loads scripts?**
The page may be behind a bot check (Cloudflare, bot management), requires JavaScript to render (SPA), or the HTML only injects scripts via JS. Try pointing the tool at the actual JS/CDN URL directly, or re-run with a larger `timeout`.

**How do I add or tweak detection patterns?**
Open `patterns.py` and add a new entry to the `PATTERNS` dict — a name and a Python regex string. The scanner picks it up automatically on the next run.

**Why do I see false positives?**
Regex-based detection is intentionally broad to avoid missing hardcoded secrets that don't follow a strict vendor format. Treat every hit as *potentially sensitive* and verify it manually before reporting it.

**Is this tool safe to run in a lab / CTF?**
Yes — it only performs unauthenticated GET requests to read public pages and JS files. No exploits, no payloads, no scanning of private pages.

## Disclaimer

This tool is intended for **security research, bug bounty programs, and defensive audits only**. Only scan targets you own or have explicit authorization to test. The author is not responsible for any misuse.

## License

Distributed under the [MIT License](LICENSE).