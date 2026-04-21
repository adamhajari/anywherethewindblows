#!/usr/bin/env python3
import requests
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import sys

BASE_URL = "https://adamhajari.com/anywherethewindblows"
visited_urls = set()
broken_links = defaultdict(list)  # link -> pages that link to it
parameterized_links = set()
working_links = set()

def is_parameterized(url):
    """Check if URL has query parameters (vestigial WordPress URLs)"""
    return '?' in urlparse(url).query or len(urlparse(url).query) > 0

def normalize_url(url):
    """Normalize URL for comparison"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def is_internal(url):
    """Check if URL is internal to the site"""
    parsed = urlparse(url)
    base_parsed = urlparse(BASE_URL)
    return parsed.netloc == base_parsed.netloc or parsed.netloc == ""

def should_crawl(url):
    """Check if we should crawl/parse this URL (skip images, media, etc.)"""
    skip_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.mp4', '.webp'}
    path = urlparse(url).path.lower()
    return not any(path.endswith(ext) for ext in skip_extensions)

def crawl(url, parent_url=None):
    """Recursively crawl site and check links"""
    # Normalize and check if already visited
    url_normalized = normalize_url(url) if url.startswith('http') else urljoin(BASE_URL, url)

    if url_normalized in visited_urls:
        return

    # Only follow internal links
    if not is_internal(url_normalized):
        return

    visited_urls.add(url_normalized)
    print(f"Crawling: {url_normalized}", end=" ... ", flush=True)

    try:
        response = requests.get(url_normalized, timeout=5, allow_redirects=True)

        # Check for parameterized URLs
        if is_parameterized(url_normalized):
            parameterized_links.add(url_normalized)
            print("PARAMETERIZED")
        elif response.status_code >= 400:
            broken_links[url_normalized].append(parent_url)
            print(f"BROKEN ({response.status_code})")
        else:
            working_links.add(url_normalized)
            print("OK")

        # Extract and follow links if page is accessible and is HTML
        if response.status_code < 400 and should_crawl(url_normalized):
            try:
                from html.parser import HTMLParser

                class LinkExtractor(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.links = []

                    def handle_starttag(self, tag, attrs):
                        if tag == 'a':
                            for attr, value in attrs:
                                if attr == 'href' and value:
                                    self.links.append(value)

                parser = LinkExtractor()
                parser.feed(response.text)

                for link in parser.links:
                    if link and not link.startswith('#'):  # Skip anchors
                        full_url = urljoin(url_normalized, link)
                        if is_internal(full_url):
                            crawl(full_url, url_normalized)
            except Exception as e:
                print(f"  Error parsing links: {e}")

    except requests.exceptions.RequestException as e:
        broken_links[url_normalized].append(parent_url)
        print(f"ERROR: {e}")

# Start crawling
print("Starting site crawl...")
crawl(BASE_URL)

# Report results
print("\n" + "="*80)
print("LINK AUDIT REPORT")
print("="*80)

# Parameterized URLs (should be treated as broken)
if parameterized_links:
    print(f"\n⚠️  PARAMETERIZED URLs (WordPress vestigial - {len(parameterized_links)}):")
    for url in sorted(parameterized_links):
        print(f"  {url}")

# Broken links
if broken_links:
    print(f"\n❌ BROKEN LINKS ({len(broken_links)}):")
    for url, referrers in sorted(broken_links.items()):
        print(f"  {url}")
        for referrer in referrers:
            if referrer:
                print(f"    ← linked from: {referrer}")

# Summary
print(f"\n📊 SUMMARY:")
print(f"  Working links: {len(working_links)}")
print(f"  Broken links: {len(broken_links)}")
print(f"  Parameterized URLs: {len(parameterized_links)}")
print(f"  Total issues: {len(broken_links) + len(parameterized_links)}")
print(f"  Pages crawled: {len(visited_urls)}")

if broken_links or parameterized_links:
    sys.exit(1)
