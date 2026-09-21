import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JSSecretFinder/1.0"
}


def get_js_files(target_url):
    """
    Fetch all JavaScript (.js) file URLs found on the target web page.

    Returns a list of absolute URLs, or an empty list when the page
    could not be accessed or no script tags are present.
    """
    js_urls = set()

    try:
        response = requests.get(target_url, headers=HEADERS, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[!] Failed to access the target URL: {e}")
        return list(js_urls)

    soup = BeautifulSoup(response.text, "html.parser")

    for script_tag in soup.find_all("script"):
        src = script_tag.attrs.get("src")
        if src:
            full_url = urljoin(target_url, src)
            if full_url.endswith(".js") or ".js?" in full_url:
                js_urls.add(full_url)

    return list(js_urls)