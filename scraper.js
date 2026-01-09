const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const cheerio = require('cheerio');

const BASE_URL = 'https://www.duttoncavanaugh.com';
const OUTPUT_DIR = './public';

async function downloadFile(url, filepath) {
  try {
    const response = await axios.get(url, {
      responseType: 'arraybuffer',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      }
    });

    const dir = path.dirname(filepath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(filepath, response.data);
    console.log(`Downloaded: ${url} -> ${filepath}`);
    return true;
  } catch (error) {
    console.error(`Failed to download ${url}:`, error.message);
    return false;
  }
}

async function scrapeWebsite() {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();

    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    console.log('Navigating to website...');
    await page.goto(BASE_URL, {
      waitUntil: 'networkidle0',
      timeout: 60000
    });

    console.log('Extracting resources...');

    const resources = await page.evaluate(() => {
      const resources = {
        stylesheets: [],
        scripts: [],
        images: [],
        links: []
      };

      document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
        resources.stylesheets.push(link.href);
      });

      document.querySelectorAll('script[src]').forEach(script => {
        resources.scripts.push(script.src);
      });

      document.querySelectorAll('img[src]').forEach(img => {
        resources.images.push(img.src);
      });

      document.querySelectorAll('a[href]').forEach(link => {
        const href = link.href;
        if (href.startsWith(window.location.origin)) {
          resources.links.push(href);
        }
      });

      return resources;
    });

    const html = await page.content();

    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    fs.writeFileSync(path.join(OUTPUT_DIR, 'index.html'), html);
    console.log('Saved index.html');

    console.log('\nDownloading stylesheets...');
    for (const cssUrl of resources.stylesheets) {
      const cssPath = new URL(cssUrl).pathname;
      await downloadFile(cssUrl, path.join(OUTPUT_DIR, cssPath));
    }

    console.log('\nDownloading scripts...');
    for (const jsUrl of resources.scripts) {
      const jsPath = new URL(jsUrl).pathname;
      await downloadFile(jsUrl, path.join(OUTPUT_DIR, jsPath));
    }

    console.log('\nDownloading images...');
    for (const imgUrl of resources.images) {
      const imgPath = new URL(imgUrl).pathname;
      await downloadFile(imgUrl, path.join(OUTPUT_DIR, imgPath));
    }

    console.log('\nDownloading additional pages...');
    const uniqueLinks = [...new Set(resources.links)];
    for (const link of uniqueLinks.slice(0, 10)) {
      try {
        const linkPath = new URL(link).pathname;
        if (linkPath !== '/' && !linkPath.includes('.')) {
          await page.goto(link, { waitUntil: 'networkidle0' });
          const pageHtml = await page.content();
          const filename = linkPath.replace(/\/$/, '') + '.html';
          fs.writeFileSync(path.join(OUTPUT_DIR, filename), pageHtml);
          console.log(`Saved ${filename}`);
        }
      } catch (error) {
        console.error(`Failed to scrape ${link}:`, error.message);
      }
    }

    console.log('\n✓ Scraping completed successfully!');
    console.log(`Files saved to: ${OUTPUT_DIR}`);

  } catch (error) {
    console.error('Error during scraping:', error);
  } finally {
    await browser.close();
  }
}

scrapeWebsite();
