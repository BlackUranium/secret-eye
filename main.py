import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from colorama import Fore, Style, init

from modules.scanner import scan_js_file
from modules.scraper import get_js_files

init(autoreset=True)

TOOL_NAME = "JS Secret & API Endpoint Finder"


def print_banner():
    banner = f"""
{Fore.CYAN}=========================================================
  {TOOL_NAME}
  Automated public JS file analysis tool that detects leaked
  secrets, API keys, tokens, and hidden internal endpoints.
========================================================={Style.RESET_ALL}
"""
    print(banner)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scan JavaScript files for leaked secrets, API keys, tokens, and hidden internal endpoints."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-u", "--url", help="Target URL to scan (e.g., https://example.com)")
    source.add_argument(
        "-l", "--list",
        help="Path to a file containing one target URL per line ('#' lines are ignored)",
    )
    parser.add_argument(
        "-o", "--output",
        help="Save the scan report to a file (.json extension enables JSON output)",
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="Force JSON report format",
    )
    parser.add_argument(
        "-t", "--threads", type=int, default=10,
        help="Number of concurrent scan threads (default: 10)",
    )
    return parser.parse_args()


def load_targets(args):
    targets = []
    if args.url:
        targets.append(args.url.rstrip("/"))
    if args.list:
        try:
            with open(args.list, "r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        targets.append(line.rstrip("/"))
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Target list not found: {args.list}{Style.RESET_ALL}")
            sys.exit(1)
    return list(dict.fromkeys(targets))


def scan_target(target, threads):
    print(f"\n{Fore.BLUE}[*] Fetching JS files from: {target}{Style.RESET_ALL}")
    js_files = get_js_files(target)

    if not js_files:
        print(f"{Fore.RED}[!] No .js files found, or the target URL could not be accessed.{Style.RESET_ALL}")
        return {"target": target, "js_files": [], "results": {}, "total_findings": 0}

    print(f"{Fore.GREEN}[+] Found {len(js_files)} JavaScript file(s).{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] Analyzing for secret leaks & endpoints...{Style.RESET_ALL}")
    print("=" * 60)

    results = {}
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_url = {
            executor.submit(scan_js_file, url): url
            for url in js_files
        }
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception:
                results[url] = {}

    return {"target": target, "js_files": js_files, "results": results, "total_findings": 0}


def display_results(target_data):
    js_files = target_data["js_files"]
    results = target_data["results"]
    total = 0

    for index, url in enumerate(js_files, start=1):
        print(f"\n{Fore.CYAN}[{index}/{len(js_files)}] Scanning: {url}{Style.RESET_ALL}")
        findings = results.get(url)
        if findings:
            for category, items in findings.items():
                print(f"   {Fore.RED}└── [!] {category}:{Style.RESET_ALL}")
                for item in items:
                    print(f"      {Fore.YELLOW}{item}{Style.RESET_ALL}")
                    total += 1
        else:
            print(f"   {Fore.GREEN}└── [✓] Clean (no secret patterns found){Style.RESET_ALL}")

    return total


def build_text_report(target_data):
    lines = []
    lines.append("=" * 60)
    lines.append(f"{TOOL_NAME} - SCAN REPORT")
    lines.append(f"Target       : {target_data['target']}")
    lines.append(f"Scan date    : {target_data['scanned_at']}")
    lines.append(f"JS files     : {len(target_data['js_files'])}")
    lines.append(f"Findings     : {target_data['total_findings']}")
    lines.append("=" * 60)

    for index, url in enumerate(target_data["js_files"], start=1):
        lines.append(f"\n[{index}/{len(target_data['js_files'])}] {url}")
        findings = target_data["results"].get(url, {})
        if findings:
            for category, items in findings.items():
                lines.append(f"   [!] {category}:")
                for item in items:
                    lines.append(f"       {item}")
        else:
            lines.append("   [✓] Clean (no secret patterns found)")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def build_json_report(target_data):
    return {
        "target": target_data["target"],
        "scanned_at": target_data["scanned_at"],
        "js_files_scanned": len(target_data["js_files"]),
        "total_findings": target_data["total_findings"],
        "findings": {
            url: findings
            for url, findings in target_data["results"].items()
            if findings
        },
    }


def main():
    print_banner()
    args = parse_args()
    targets = load_targets(args)

    reports = []
    for target in targets:
        data = scan_target(target, args.threads)
        data["scanned_at"] = datetime.now().isoformat(timespec="seconds")
        total = display_results(data)
        data["total_findings"] = total
        reports.append(data)

        print()
        if total > 0:
            print(f"{Fore.RED}[!] Scan complete! Total potential secrets detected: {total}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[✓] Scan complete! No leaked secrets/tokens found in the JS files.{Style.RESET_ALL}")

    use_json = args.json_output or (args.output and args.output.lower().endswith(".json"))
    if args.output:
        if use_json:
            payload = {
                "tool": TOOL_NAME,
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "targets": [build_json_report(report) for report in reports],
            }
            content = json.dumps(payload, indent=2)
        else:
            content = "\n\n".join(build_text_report(report) for report in reports)

        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(content)
        print(f"{Fore.GREEN}[+] Report saved to: {args.output}{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Scan interrupted by user.{Style.RESET_ALL}")
        sys.exit(130)