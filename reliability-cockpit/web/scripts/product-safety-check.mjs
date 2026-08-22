import { readdir, readFile } from "node:fs/promises";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const sourceRoots = [join(webRoot, "app"), join(webRoot, "components")];

async function sourceFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await sourceFiles(path));
    else if (entry.name.endsWith(".tsx")) files.push(path);
  }
  return files;
}

const files = (await Promise.all(sourceRoots.map(sourceFiles))).flat();
const failures = [];
const countLiterals = [
  /\b845\s+Registered Reliability Assets\b/,
  /\b100\s+FMEA\b/,
  /\b100\s+RCFA\b/,
  /\b100\s+Asset Health\b/,
  /\b1\s+Overhaul\b/,
];

for (const file of files) {
  const source = await readFile(file, "utf8");
  const name = relative(webRoot, file);
  for (const pattern of countLiterals) {
    if (pattern.test(source)) failures.push(`${name}: hardcoded live business count matches ${pattern}`);
  }
  for (const line of source.split("\n")) {
    if (line.includes("<StatusBadge") && !line.includes("mode=")) failures.push(`${name}: StatusBadge usage must declare an explicit mode`);
  }
}

const ui = await readFile(join(webRoot, "components", "ui.tsx"), "utf8");
const css = await readFile(join(webRoot, "app", "globals.css"), "utf8");
if (!ui.includes('{ href: "/data-quality", label: "Data Trust"')) failures.push("ui.tsx: Data Trust navigation label missing");
if (ui.includes('{ href: "/data-quality", label: "Data Quality"')) failures.push("ui.tsx: stale Data Quality navigation label remains");
if (!ui.includes("pathname.startsWith(item.href)")) failures.push("ui.tsx: nested route active-state logic missing");
if (!ui.includes('mode = "raw-neutral"')) failures.push("ui.tsx: StatusBadge default must be raw-neutral");
if (!ui.includes("Data Reliability Mart belum dapat dibaca")) failures.push("ui.tsx: user-readable Reliability Mart error copy missing");
if (ui.includes("Data canonical belum dapat dibaca")) failures.push("ui.tsx: stale canonical error copy remains");
if (!ui.includes('aria-label="Previous page"') || !ui.includes('aria-label="Next page"')) failures.push("ui.tsx: pagination accessibility labels missing");
if (!css.includes(":focus-visible")) failures.push("globals.css: visible keyboard focus treatment missing");

if (failures.length > 0) {
  console.error("Product safety check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exitCode = 1;
} else {
  console.log(`Product safety check passed for ${files.length} UI source files`);
}
