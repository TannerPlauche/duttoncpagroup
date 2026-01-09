#!/usr/bin/env python3
"""
Selenium-based scraper for duttoncavanaugh.com
Uses a real browser to bypass anti-bot measures
"""

import os
import time
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("ERROR: Selenium not installed.")
    print("Install with: pip3 install selenium")
    exit(1)

BASE_URL = "https://www.duttoncavanaugh.com"
OUTPUT_DIR = "./public"
VISITED_URLS = set()


def setup_driver():
    """Setup Chrome driver with options to avoid detection"""
    options = Options()
    # Run headless
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def get_local_filename(url, base_url):
    """Convert URL to local filename"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')

    if not path:
        return 'index.html'

    # If it's a page (no extension), add .html
    if '.' not in os.path.basename(path):
        return f"{path}.html"

    return path


def save_page(driver, url, output_path):
    """Save a page's HTML content"""
    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        html_content = driver.page_source

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ Saved: {url}")
        print(f"  → {output_path}")
        return True

    except Exception as e:
        print(f"✗ Error saving {url}: {e}")
        return False


def get_internal_links(driver, base_url):
    """Extract all internal links from current page"""
    links = set()

    try:
        # Find all anchor tags
        elements = driver.find_elements(By.TAG_NAME, 'a')

        for element in elements:
            try:
                href = element.get_attribute('href')
                if href:
                    # Make absolute
                    absolute_url = urljoin(base_url, href)

                    # Check if same domain
                    if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                        # Remove fragment
                        absolute_url = absolute_url.split('#')[0]
                        if absolute_url:
                            links.add(absolute_url)

            except Exception:
                continue

    except Exception as e:
        print(f"Error extracting links: {e}")

    return links


def scrape_website(start_url, max_pages=20):
    """Main scraping function"""
    print("=" * 60)
    print("Dutton Cavanaugh Website Scraper (Selenium)")
    print("=" * 60)
    print(f"Base URL: {start_url}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Max pages: {max_pages}")
    print("\nStarting browser...\n")

    driver = setup_driver()
    to_visit = {start_url}
    pages_scraped = 0

    try:
        while to_visit and pages_scraped < max_pages:
            url = to_visit.pop()

            if url in VISITED_URLS:
                continue

            VISITED_URLS.add(url)
            print(f"\n[{pages_scraped + 1}/{max_pages}] Visiting: {url}")

            try:
                driver.get(url)

                # Wait for page to load
                time.sleep(2)

                # Save the page
                local_filename = get_local_filename(url, start_url)
                output_path = os.path.join(OUTPUT_DIR, local_filename)

                if save_page(driver, url, output_path):
                    pages_scraped += 1

                # Find more links
                new_links = get_internal_links(driver, start_url)
                to_visit.update(new_links - VISITED_URLS)

                print(f"  Found {len(new_links)} links on this page")

            except Exception as e:
                print(f"✗ Error visiting {url}: {e}")

            # Be polite - add delay between requests
            time.sleep(1)

    finally:
        driver.quit()

    print("\n" + "=" * 60)
    print("Scraping Complete!")
    print("=" * 60)
    print(f"Total pages scraped: {pages_scraped}")
    print(f"Files saved to: {os.path.abspath(OUTPUT_DIR)}")
    print("\nStart the server with: npm start")
    print("Then visit: http://localhost:3000")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    scrape_website(BASE_URL, max_pages=20)
