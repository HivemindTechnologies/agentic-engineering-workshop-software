// Print a served reveal.js deck to PDF via the bundled Puppeteer.
// Usage: node .bin/_print.mjs <url> <out.pdf>
// Waits for the markdown plugin to finish splitting slides before printing —
// reveal-md's own --print fires too early on large data-markdown decks.

import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import puppeteer from "puppeteer";

const [url, out] = process.argv.slice(2);
if (!url || !out) {
  console.error("usage: _print.mjs <url> <out.pdf>");
  process.exit(2);
}

// Pick a browser: a system Chromium first, because a Puppeteer-downloaded
// Chrome is unpatched and does not start on NixOS (it cannot load libglib).
// PUPPETEER_EXECUTABLE_PATH overrides both.
function findBrowser() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) return process.env.PUPPETEER_EXECUTABLE_PATH;
  for (const name of ["chromium", "chrome", "google-chrome-stable", "google-chrome"]) {
    try {
      return execFileSync("which", [name], { encoding: "utf8" }).trim();
    } catch {}
  }
  try {
    const own = puppeteer.executablePath();
    if (existsSync(own)) return own;
  } catch {}
  return undefined;
}

const executablePath = findBrowser();
if (executablePath) console.log(`  browser: ${executablePath}`);

const browser = await puppeteer.launch({
  headless: true,
  executablePath,
  // --use-gl=swiftshader keeps rendering in-process: a sandbox that hides
  // /sys/bus/pci kills the GPU process, and Chromium then aborts on startup.
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--use-gl=swiftshader"],
});
try {
  const page = await browser.newPage();
  await page.goto(`${url}?print-pdf`, { waitUntil: "networkidle0", timeout: 60000 });

  // Wait until slide count stops growing (markdown split done), then let
  // reveal.js run its print-pdf layout pass.
  let last = -1;
  for (let i = 0; i < 60; i++) {
    const n = await page.evaluate(
      () => document.querySelectorAll(".reveal .slides section:not(.stack)").length,
    );
    if (n > 0 && n === last) break;
    last = n;
    await new Promise((r) => setTimeout(r, 250));
  }
  // reveal.js runs its print-pdf pagination once, before the markdown plugin
  // has finished splitting slides. Re-run it now that all sections exist.
  const size = await page.evaluate(async () => {
    const cfg = window.Reveal?.getConfig?.() ?? {};
    const slideW = cfg.width ?? 960;
    const slideH = cfg.height ?? 700;
    const margin = cfg.margin ?? 0.04;
    const pageW = Math.floor(slideW * (1 + margin));
    const pageH = Math.floor(slideH * (1 + margin));

    // Reset anything the early pass wrapped, then lay every slide onto its page.
    document.documentElement.classList.add("reveal-print", "print-pdf");
    const slides = [...document.querySelectorAll(".reveal .slides section")].filter(
      (s) => !s.classList.contains("stack"),
    );
    // Each slide gets a .pdf-page box, the shape theme/print-pdf.css styles:
    // the page breaks after it and clips, the slide is absolute inside it.
    for (const s of slides) {
      const pdfPage = document.createElement("div");
      pdfPage.className = "pdf-page";
      pdfPage.style.width = pageW + "px";
      pdfPage.style.height = pageH + "px";
      s.parentNode.insertBefore(pdfPage, s);
      pdfPage.appendChild(s);
      s.style.width = slideW + "px";
      s.style.left = (pageW - slideW) / 2 + "px";
      s.style.height = "auto";
      s.style.boxSizing = "border-box";
    }
    // Second pass, after the first one has settled the widths: centre each
    // slide vertically the way reveal's center:true does on screen, by the
    // measured content height rather than the nominal slide height.
    for (const s of slides) {
      s.style.top = Math.max((pageH - s.offsetHeight) / 2, 0) + "px";
    }
    const slidesEl = document.querySelector(".reveal .slides");
    slidesEl.style.cssText =
      "position:static;width:" + pageW + "px;height:auto;left:0;top:0;transform:none;display:block;";
    const revealEl = document.querySelector(".reveal");
    revealEl.style.cssText = "position:static;width:" + pageW + "px;height:auto;overflow:visible;";
    document.documentElement.style.cssText = "width:" + pageW + "px;height:auto;overflow:visible;";
    document.body.style.cssText =
      "width:" + pageW + "px;height:auto;overflow:visible;margin:0;position:static;";
    return { pageW, pageH, count: slides.length, bodyH: document.body.scrollHeight };
  });
  await new Promise((r) => setTimeout(r, 800));
  console.log(`  layout: ${size.count} slides, page ${size.pageW}x${size.pageH}, body ${size.bodyH}px`);

  await page.pdf({
    path: out,
    printBackground: true,
    width: `${size.pageW}px`,
    height: `${size.pageH}px`,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
    pageRanges: `1-${size.count}`,
    timeout: 180000,
  });
  console.log(`wrote ${out} (${size.count} pages)`);
} finally {
  await browser.close();
}
