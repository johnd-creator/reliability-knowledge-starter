/** @type {import('next').NextConfig} */
const nextConfig = {
  // Keep dev output isolated so a production build cannot leave a partial
  // App Router manifest in the directory used by `next dev`.
  distDir: process.env.NODE_ENV === "development" ? (process.env.NADI_PRIMARY_FRONTEND === "true" ? ".next-primary-dev" : ".next-dev") : ".next",
  outputFileTracingRoot: __dirname,
  // FIX-03 isolated A/B: avoid development filesystem-pack serialization/cache
  // retention. Keep HMR and Next's own GC cache/memory restart safeguard.
  // Production has no custom webpack hook, preserving its build-worker behavior.
  ...(process.env.NODE_ENV === "development" ? {
    webpack(config, { dev }) {
      if (dev) config.cache = false;
      return config;
    },
  } : {}),
  async rewrites() {
    return [
      {
        source: "/api/cockpit/:path*",
        destination: `${process.env.COCKPIT_API_BASE || "http://127.0.0.1:8000"}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
