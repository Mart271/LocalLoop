// Development-only smoke test of the actual Tauri WebView2, including the isolation hook.
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { randomUUID } from "node:crypto";
import { createServer } from "node:net";

const require = createRequire(resolve(".localloop-dev/tooling/package.json"));
const puppeteer = require("puppeteer");
const reservation = createServer();
await new Promise((ready, failed) => { reservation.once("error", failed); reservation.listen(0, "127.0.0.1", ready); });
const port = reservation.address().port;
await new Promise(ready => reservation.close(ready));
const started = performance.now();
const app = spawn(resolve("target/debug/localloop.exe"), [], {
  windowsHide: true,
  env: { ...process.env, LOCALLOOP_STRICT_OFFLINE: "1",
    WEBVIEW2_USER_DATA_FOLDER: resolve(".localloop-dev/webview", randomUUID()),
    WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS: `--remote-debugging-port=${port} --remote-debugging-address=127.0.0.1` },
  stdio: "ignore",
});
let browser;
try {
  let lastError;
  while (performance.now() - started < 30000) {
    if (app.exitCode !== null) throw new Error(`App exited: ${app.exitCode}`);
    try { browser = await puppeteer.connect({ browserURL: `http://127.0.0.1:${port}`, defaultViewport: null }); break; }
    catch (error) { lastError = error; await new Promise(r => setTimeout(r, 100)); }
  }
  if (!browser) throw lastError;
  let page;
  while (performance.now() - started < 30000) {
    page = (await browser.pages()).find(p => p.url().includes("tauri.localhost"));
    if (page) break;
    await new Promise(r => setTimeout(r, 100));
  }
  if (!page) throw new Error(`No application WebView: ${(await browser.pages()).map(p => p.url()).join(", ")}`);
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.waitForFunction(() => document.querySelector('[role="status"]')?.textContent?.includes("Connected (version 0.1.0)"), { timeout: 15000 });
  const startupToConnectedMs = performance.now() - started;
  const isolationHidden = await page.$eval("iframe#__tauri_isolation__", frame => getComputedStyle(frame).display === "none");
  if (!isolationHidden) throw new Error("Tauri isolation iframe is visible under the strict CSP");
  await page.click("button");
  await page.waitForFunction(() => document.querySelector('[role="status"]')?.textContent?.includes("Connected (version 0.1.0)"), { timeout: 15000 });
  const text = await page.$eval("main", element => element.textContent);
  await mkdir("test-results", { recursive: true });
  await page.screenshot({ path: "test-results/windows-shell.png" });
  const report = { recorded_at_utc: new Date().toISOString(), executable: "target/debug/localloop.exe", build_profile: "debug",
    startup_to_connected_ms: Math.round(startupToConnectedMs), status: "connected", recheck: "connected",
    isolation_hidden: isolationHidden, page_errors: errors, ui_text: text, method: "Actual WebView2 via temporary loopback debugging; development setting only; fresh WebView profile, warm OS caches; readiness timing includes debugger polling overhead and uncontrolled background work; no reference-machine claim" };
  await writeFile("docs/development/spikes/evidence/windows-smoke.json", JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
  if (errors.length) throw new Error(`WebView errors: ${errors.join(", ")}`);
} finally {
  if (browser) browser.disconnect();
  // This test owns only this process. WebView descendants should close when it exits.
  app.kill();
}
