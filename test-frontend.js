/**
 * Puppeteer script to test the frontend and take screenshots
 */

import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function testFrontend() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });

    console.log('🚀 Testing frontend at http://localhost:5173...');
    
    // Navigate to the frontend
    await page.goto('http://localhost:5173', { 
      waitUntil: 'networkidle2',
      timeout: 10000 
    });

    // Wait for React to render
    await page.waitForSelector('#root', { timeout: 5000 });

    // Check if the main title is rendered
    const title = await page.$eval('h1', el => el.textContent).catch(() => null);
    console.log(`📄 Page title: ${title || 'Not found'}`);

    // Check if the voice button exists
    const buttonExists = await page.$('button') !== null;
    console.log(`🎤 Voice button exists: ${buttonExists}`);

    // Take a screenshot
    const screenshotPath = path.join(__dirname, 'frontend-screenshot.png');
    await page.screenshot({ 
      path: screenshotPath,
      fullPage: true 
    });
    console.log(`📸 Screenshot saved to: ${screenshotPath}`);

    // Check for any console errors
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Wait a bit to catch any errors
    await new Promise(resolve => setTimeout(resolve, 2000));

    if (errors.length > 0) {
      console.log('❌ Console errors found:');
      errors.forEach(error => console.log(`   - ${error}`));
    } else {
      console.log('✅ No console errors detected');
    }

    // Test Tailwind styles by checking if classes are applied
    const hasStyledElements = await page.evaluate(() => {
      const elements = document.querySelectorAll('[class*="bg-"], [class*="text-"], [class*="p-"], [class*="m-"]');
      return elements.length > 0;
    });
    console.log(`🎨 Tailwind styles detected: ${hasStyledElements}`);

    return {
      success: true,
      title,
      buttonExists,
      hasStyledElements,
      screenshotPath,
      errors
    };

  } catch (error) {
    console.error('❌ Frontend test failed:', error.message);
    return {
      success: false,
      error: error.message
    };
  } finally {
    await browser.close();
  }
}

// Run the test
testFrontend().then(result => {
  console.log('\n📊 Test Results:');
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.success ? 0 : 1);
});