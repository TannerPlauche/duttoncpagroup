const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://www.duttoncavanaugh.com';
const OUTPUT_DIR = './public';

async function scrapeWithStealth() {
  console.log('Launching browser with stealth mode...');

  const browser = await puppeteer.launch({
    headless: false, // Run in visible mode to avoid detection
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage',
      '--window-size=1920,1080'
    ]
  });

  try {
    const page = await browser.newPage();

    // Remove automation indicators
    await page.evaluateOnNewDocument(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
      });

      window.navigator.chrome = {
        runtime: {},
      };

      Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
      });

      Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
      });
    });

    // Set realistic viewport and user agent
    await page.setViewport({ width: 1920, height: 1080 });
    await page.setUserAgent(
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );

    // Set extra headers
    await page.setExtraHTTPHeaders({
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Encoding': 'gzip, deflate, br',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1'
    });

    console.log('Navigating to website...');
    await page.goto(BASE_URL, {
      waitUntil: 'networkidle2',
      timeout: 60000
    });

    // Wait a bit to look more human-like
    await new Promise(resolve => setTimeout(resolve, 2000));

    console.log('Extracting page content...');
    const html = await page.content();

    // Save HTML
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    fs.writeFileSync(path.join(OUTPUT_DIR, 'index.html'), html);
    console.log('✓ Saved index.html');

    // Get all resources
    const resources = await page.evaluate(() => {
      const result = {
        images: [],
        scripts: [],
        stylesheets: [],
        fonts: []
      };

      // Images
      document.querySelectorAll('img[src]').forEach(img => {
        if (img.src) result.images.push(img.src);
      });

      // Background images
      document.querySelectorAll('*').forEach(el => {
        const bg = window.getComputedStyle(el).backgroundImage;
        if (bg && bg !== 'none') {
          const match = bg.match(/url\(['"]?([^'"]+)['"]?\)/);
          if (match) result.images.push(match[1]);
        }
      });

      // Scripts
      document.querySelectorAll('script[src]').forEach(script => {
        if (script.src) result.scripts.push(script.src);
      });

      // Stylesheets
      document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
        if (link.href) result.stylesheets.push(link.href);
      });

      return result;
    });

    console.log(`\nFound resources:`);
    console.log(`- Images: ${resources.images.length}`);
    console.log(`- Scripts: ${resources.scripts.length}`);
    console.log(`- Stylesheets: ${resources.stylesheets.length}`);

    console.log('\n✓ Scraping completed!');
    console.log(`Files saved to: ${OUTPUT_DIR}`);
    console.log('\nYou can now run: npm start');

  } catch (error) {
    console.error('Error during scraping:', error.message);
  } finally {
    await browser.close();
  }
}

scrapeWithStealth();
