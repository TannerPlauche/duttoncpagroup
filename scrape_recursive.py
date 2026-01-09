#!/usr/bin/env python3
"""
Recursive web scraper for duttoncavanaugh.com
Downloads all pages and their assets
"""

import os
import re
import time
import urllib.request
import urllib.parse
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
from pathlib import Path

BASE_URL = "https://www.duttoncavanaugh.com"
OUTPUT_DIR = "./public"
VISITED_URLS = set()
DOWNLOADED_FILES = set()

class LinkParser(HTMLParser):
    """Parser to extract links from HTML"""
    def __init__(self):
        super().__init__()
        self.links = []
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Extract page links
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append(attrs_dict['href'])

        # Extract assets
        if tag == 'img' and 'src' in attrs_dict:
            self.assets.append(attrs_dict['src'])
        elif tag == 'link' and 'href' in attrs_dict:
            self.assets.append(attrs_dict['href'])
        elif tag == 'script' and 'src' in attrs_dict:
            self.assets.append(attrs_dict['src'])


def get_local_path(url, base_url):
    """Convert URL to local file path"""
    parsed = urlparse(url)
    path = parsed.path

    if not path or path == '/':
        return 'index.html'

    # Remove leading slash
    path = path.lstrip('/')

    # If no extension, treat as HTML page
    if '.' not in os.path.basename(path):
        path = f"{path}.html" if not path.endswith('/') else f"{path}index.html"

    return path


def download_file(url, output_path):
    """Download a file from URL to output path"""
    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()

            with open(output_path, 'wb') as f:
                f.write(content)

            print(f"✓ Downloaded: {url}")
            print(f"  → {output_path}")
            return content

    except Exception as e:
        print(f"✗ Failed to download {url}: {e}")
        return None


def is_same_domain(url, base_url):
    """Check if URL is from the same domain"""
    return urlparse(url).netloc == urlparse(base_url).netloc or not urlparse(url).netloc


def normalize_url(url, base_url):
    """Normalize and make URL absolute"""
    # Handle empty or None URLs
    if not url:
        return None

    # Remove fragments
    url = url.split('#')[0]

    # Make absolute
    url = urljoin(base_url, url)

    # Only return if same domain
    if is_same_domain(url, base_url):
        return url

    return None


def scrape_page(url, base_url, depth=0, max_depth=3):
    """Recursively scrape a page and its links"""

    if depth > max_depth:
        print(f"⊗ Max depth reached for: {url}")
        return

    if url in VISITED_URLS:
        return

    VISITED_URLS.add(url)
    print(f"\n{'  ' * depth}📄 Scraping (depth {depth}): {url}")

    # Get local file path
    local_path = get_local_path(url, base_url)
    output_path = os.path.join(OUTPUT_DIR, local_path)

    # Download the page
    content = download_file(url, output_path)

    if not content:
        return

    # Parse HTML to find links
    try:
        html_content = content.decode('utf-8', errors='ignore')
        parser = LinkParser()
        parser.feed(html_content)

        # Process page links recursively
        for link in parser.links:
            normalized_link = normalize_url(link, url)
            if normalized_link and normalized_link not in VISITED_URLS:
                # Add a small delay to be polite
                time.sleep(0.5)
                scrape_page(normalized_link, base_url, depth + 1, max_depth)

        # Download assets
        for asset in parser.assets:
            normalized_asset = normalize_url(asset, url)
            if normalized_asset and normalized_asset not in DOWNLOADED_FILES:
                DOWNLOADED_FILES.add(normalized_asset)
                asset_path = get_local_path(normalized_asset, base_url)
                asset_output = os.path.join(OUTPUT_DIR, asset_path)
                time.sleep(0.2)  # Small delay
                download_file(normalized_asset, asset_output)

    except Exception as e:
        print(f"✗ Error parsing {url}: {e}")


def main():
    print("=" * 60)
    print("Dutton Cavanaugh Website Scraper")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Starting recursive scrape...\n")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Start scraping from home page
    scrape_page(BASE_URL, BASE_URL, depth=0, max_depth=3)

    print("\n" + "=" * 60)
    print("Scraping Complete!")
    print("=" * 60)
    print(f"Total pages visited: {len(VISITED_URLS)}")
    print(f"Total files downloaded: {len(DOWNLOADED_FILES)}")
    print(f"\nFiles saved to: {os.path.abspath(OUTPUT_DIR)}")
    print("\nStart the server with: npm start")
    print("Then visit: http://localhost:3000")


if __name__ == "__main__":
    main()
