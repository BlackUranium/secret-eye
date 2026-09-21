# JS Secret & API Endpoint Finder

Automated tool that crawls a target website's public JavaScript files and hunts for **leaked secrets, API keys, tokens, and hidden internal endpoints**.

Frontend bundles often ship production credentials straight to the browser. This tool detects those leaks using a curated set of regex patterns and reports them per JS file — useful for bug bounty, pentesting, and defensive audits.

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

## Disclaimer

This tool is intended for **security research, bug bounty programs, and defensive audits only**. Only scan targets you own or have explicit authorization to test. The author is not responsible for any misuse.

## License

MIT