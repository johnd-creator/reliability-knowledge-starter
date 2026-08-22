const baseUrl = (process.env.NADI_WEB_BASE_URL || "http://127.0.0.1:3000").replace(/\/$/, "");
const routes = ["/", "/assets", "/maintenance", "/maintenance/investigation", "/fmea", "/rcfa", "/asset-health", "/overhauls", "/data-quality"];
const navigationHrefs = ["/", "/assets", "/maintenance", "/fmea", "/rcfa", "/asset-health", "/overhauls", "/data-quality"];

const failures = [];
for (const route of routes) {
  const response = await fetch(`${baseUrl}${route}`);
  const body = await response.text();
  if (!response.ok) failures.push(`${route}: HTTP ${response.status}`);
  if (!body.includes("NADI")) failures.push(`${route}: NADI shell marker missing`);
  if (route === "/") {
    for (const href of navigationHrefs) {
      if (!body.includes(`href="${href}"`)) failures.push(`/: sidebar href missing: ${href}`);
    }
  }
  console.log(`${response.ok ? "PASS" : "FAIL"} ${route} HTTP ${response.status}`);
}

if (failures.length) {
  console.error("Route smoke failures:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exitCode = 1;
} else {
  console.log(`Route smoke passed for ${routes.length} routes at ${baseUrl}`);
}
