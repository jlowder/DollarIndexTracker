
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Set up a listener for console messages
  page.on('console', msg => console.log('BROWSER LOG:', msg.text()));

  // Navigate to the file
  const filePath = `file://${process.cwd()}/dollar_index_tracker.html`;
  console.log(`Opening ${filePath}`);
  await page.goto(filePath);

  const periods = ['1y', '2y', '5y', '10y', 'max'];

  for (const period of periods) {
    console.log(`\nTesting period: ${period}`);

    // Select the period
    await page.selectOption('#timePeriod', period);

    // Wait for the data to load or fail
    // We'll wait up to 30 seconds because of the multi-proxy fallback and 10s timeouts
    try {
      await page.waitForFunction(() => {
        const metrics = document.getElementById('metricsContainer').innerText;
        return metrics && !metrics.includes('Loading metrics...');
      }, { timeout: 45000 });

      const isSimulated = await page.evaluate(() => !!document.getElementById('simulationWarning'));
      console.log(`Result for ${period}: ${isSimulated ? 'SIMULATED (Fail)' : 'LIVE (Success)'}`);

      if (isSimulated) {
        // Log the error message if any
        const errorMsg = await page.evaluate(() => {
            const errDiv = document.querySelector('.error');
            return errDiv ? errDiv.innerText : 'No error div found';
        });
        console.log(`Error message: ${errorMsg}`);
      }
    } catch (e) {
      console.log(`Timeout waiting for ${period}: ${e.message}`);
    }
  }

  await browser.close();
})();
