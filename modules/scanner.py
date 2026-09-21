import re

import requests

from patterns import PATTERNS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JSSecretFinder/1.0"
}


def scan_js_file(js_url):
    """Download a JS file and scan it for leaked secrets using the regex patterns in patterns.py."""
    findings = {}

    try:
        response = requests.get(js_url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            return findings

        content = response.text

        for pattern_name, regex in PATTERNS.items():
            matches = re.findall(regex, content)
            if not matches:
                continue

            unique_matches = []
            for match in matches:
                value = match[1] if isinstance(match, tuple) else match
                if value not in unique_matches:
                    unique_matches.append(value)

            findings[pattern_name] = unique_matches

    except requests.exceptions.RequestException:
        pass

    return findings