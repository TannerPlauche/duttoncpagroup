#!/usr/bin/env python3
"""
BeautifulSoup-based recursive scraper for duttoncavanaugh.com
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path

BASE_URL = "https://www.duttoncavanaugh.com"
OUTPUT_DIR = "./public"
VISITED_URLS = set()

# Session with headers to mimic a real browser
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
})


def get_local_filename(url, base_url):
    """Convert URL to local filename"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')

    if not path:
        return 'index.html'

    # If it's a page (no extension), add .html
    if '.' not in os.path.basename(path):
        return f"{path.replace('/', '-')}.html"

    return path


def download_page(url):
    """Download a page with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=30, allow_redirects=True)

            if response.status_code == 403:
                print(f"⚠ Access forbidden (403) for: {url}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                return None

            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            print(f"✗ Error downloading {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None

    return None


def save_page(url, html_content, output_path):
    """Save HTML content to file"""
    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else OUTPUT_DIR, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ Saved: {url}")
        print(f"  → {output_path}")
        return True

    except Exception as e:
        print(f"✗ Error saving {url}: {e}")
        return False


def extract_links(html_content, base_url):
    """Extract all internal links from HTML"""
    links = set()

    try:
        soup = BeautifulSoup(html_content, 'lxml')

        # Find all anchor tags
        for tag in soup.find_all('a', href=True):
            href = tag['href']

            # Make absolute URL
            absolute_url = urljoin(base_url, href)

            # Remove fragment
            absolute_url = absolute_url.split('#')[0]

            # Check if same domain
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                # Skip certain file types
                if not any(absolute_url.lower().endswith(ext) for ext in ['.pdf', '.zip', '.jpg', '.png', '.gif', '.css', '.js']):
                    links.add(absolute_url)

    except Exception as e:
        print(f"Error parsing HTML: {e}")

    return links


def scrape_recursive(url, base_url, depth=0, max_depth=3, max_pages=50):
    """Recursively scrape website"""

    if depth > max_depth:
        print(f"⊗ Max depth reached for: {url}")
        return

    if len(VISITED_URLS) >= max_pages:
        print(f"⊗ Max pages limit reached")
        return

    if url in VISITED_URLS:
        return

    VISITED_URLS.add(url)

    indent = "  " * depth
    print(f"\n{indent}[{len(VISITED_URLS)}/{max_pages}] 📄 Scraping (depth {depth}): {url}")

    # Download the page
    html_content = download_page(url)

    if not html_content:
        return

    # Save the page
    local_filename = get_local_filename(url, base_url)
    output_path = os.path.join(OUTPUT_DIR, local_filename)
    save_page(url, html_content, output_path)

    # Extract and follow links
    links = extract_links(html_content, url)
    print(f"{indent}  Found {len(links)} internal links")

    for link in links:
        if len(VISITED_URLS) >= max_pages:
            break

        if link not in VISITED_URLS:
            # Be polite - delay between requests
            time.sleep(1)
            scrape_recursive(link, base_url, depth + 1, max_depth, max_pages)


def main():
    print("=" * 70)
    print("Dutton Cavanaugh Website Scraper (BeautifulSoup)")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("\nStarting recursive scrape...\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Start scraping
    scrape_recursive(BASE_URL, BASE_URL, depth=0, max_depth=2, max_pages=30)

    print("\n" + "=" * 70)
    print("Scraping Complete!")
    print("=" * 70)
    print(f"Total pages scraped: {len(VISITED_URLS)}")
    print(f"Files saved to: {os.path.abspath(OUTPUT_DIR)}")
    print("\nStart the server with: npm start")
    print("Then visit: http://localhost:3000")


if __name__ == "__main__":
    main()
