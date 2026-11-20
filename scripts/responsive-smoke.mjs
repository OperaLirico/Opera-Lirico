import { chromium } from "playwright";

const base = (process.argv[2] || "http://127.0.0.1:4173").replace(/\/$/, "");
const pages = [
  "index.html",
  "masterclasses.html",
  "voice-anatomy.html",
  "larynx-mechanism.html",
  "voice-lab.html",
];
const viewports = [
  { width: 1440, height: 900 },
  { width: 1024, height: 768 },
  { width: 768, height: 1024 },
  { width: 390, height: 844 },
];

const browser = await chromium.launch({
  headless: true,
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
});
const failures = [];
const pageErrors = [];

for (const path of pages) {
  for (const viewport of viewports) {
    const page = await browser.newPage({ viewport });
    page.setDefaultTimeout(7000);
    page.on("pageerror", (error) => pageErrors.push(`${path}: ${error.message}`));

    try {
      const response = await page.goto(`${base}/${path}`, {
        waitUntil: "domcontentloaded",
        timeout: 45000,
      });
      if (!response || !response.ok()) {
        failures.push(`${path} [${viewport.width}]: HTTP ${response?.status() ?? "no response"}`);
      }
      await page.waitForTimeout(500);

      const result = await page.evaluate(() => {
        const width = window.innerWidth;
        const rootWidth = Math.max(
          document.documentElement?.scrollWidth || 0,
          document.body?.scrollWidth || 0
        );
        const frameEdges = [...document.querySelectorAll("header, main, footer")]
          .filter((element) => {
            const style = getComputedStyle(element);
            return style.display !== "none" && style.visibility !== "hidden";
          })
          .map((element) => {
            const rect = element.getBoundingClientRect();
            return {
              element: element.tagName.toLowerCase() + (element.id ? "#" + element.id : ""),
              left: Math.round(rect.left),
              right: Math.round(rect.right),
            };
          })
          .filter((rect) => rect.left < -2 || rect.right > width + 2);
        const missingAnchors = [...document.querySelectorAll('a[href^="#"]')]
          .map((link) => link.getAttribute("href"))
          .filter((href) => href && href.length > 1)
          .filter((href) => {
            try {
              return !document.getElementById(decodeURIComponent(href.slice(1)));
            } catch {
              return true;
            }
          });
        return {
          title: document.title,
          hasMain: Boolean(document.querySelector("main")),
          hasViewport: Boolean(document.querySelector('meta[name="viewport"]')),
          rootWidth,
          width,
          frameEdges,
          missingAnchors: [...new Set(missingAnchors)],
        };
      });

      if (!result.hasMain) failures.push(`${path} [${viewport.width}]: missing main landmark`);
      if (!result.hasViewport) failures.push(`${path} [${viewport.width}]: missing viewport meta`);
      if (result.rootWidth > result.width + 2) {
        failures.push(`${path} [${viewport.width}]: horizontal overflow (${result.rootWidth}px > ${result.width}px)`);
      }
      for (const edge of result.frameEdges) {
        failures.push(`${path} [${viewport.width}]: ${edge.element} outside viewport (${edge.left}–${edge.right}px)`);
      }
      for (const href of result.missingAnchors) {
        failures.push(`${path} [${viewport.width}]: broken in-page link ${href}`);
      }
      if (!result.title.trim()) failures.push(`${path} [${viewport.width}]: empty document title`);
    } catch (error) {
      failures.push(`${path} [${viewport.width}]: ${error.message}`);
    } finally {
      await page.close();
    }
  }
}

async function interactionCheck(path, selector, label, verify) {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  page.setDefaultTimeout(7000);
  page.on("pageerror", (error) => pageErrors.push(`${path} interaction: ${error.message}`));
  try {
    await page.goto(`${base}/${path}`, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForTimeout(900);
    const control = page.locator(selector).first();
    if (await control.count()) {
      await control.click();
      const passed = await verify(page);
      if (!passed) failures.push(`${path}: interaction did not respond — ${label}`);
    } else {
      failures.push(`${path}: expected interactive control not found — ${label}`);
    }
  } catch (error) {
    failures.push(`${path}: interaction check failed — ${label}: ${error.message}`);
  } finally {
    await page.close();
  }
}

await interactionCheck(
  "index.html",
  '.tile[data-open="open-calls"]',
  "open the auditions and competitions panel",
  (page) => page.locator("#open-calls").evaluate((element) => !element.hidden)
);
await interactionCheck(
  "masterclasses.html",
  'a[href="#masterList"]',
  "navigate to the verified course list",
  (page) => page.evaluate(() => location.hash === "#masterList")
);
await interactionCheck(
  "voice-anatomy.html",
  "[data-organ-select]",
  "select an anatomy structure",
  (page) => page.locator("[data-organ-select]").first().getAttribute("aria-pressed").then((value) => value === "true")
);
await interactionCheck(
  "larynx-mechanism.html",
  '[data-mode="lca"]',
  "switch the laryngeal mechanism",
  (page) => page.locator('[data-mode="lca"]').getAttribute("aria-pressed").then((value) => value === "true")
);
await interactionCheck(
  "voice-lab.html",
  "#list .item",
  "select a vocal structure",
  (page) => page.locator("#detail").evaluate((element) => element.textContent.trim().length > 0)
);

await browser.close();

for (const error of pageErrors) failures.push(`JavaScript runtime error: ${error}`);

console.log(`Checked ${pages.length} pages at ${viewports.length} viewport widths and exercised 5 key interactions.`);
if (failures.length) {
  console.error(`Responsive smoke test failed with ${failures.length} issue(s):`);
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}
console.log("Responsive layout, in-page links, and key interactions passed.");
