/** @type {import('next').NextConfig} */
const nextConfig = {
  // Keep dev output isolated so a production build cannot leave a partial
  // App Router manifest in the directory used by `next dev`.
  distDir: process.env.NODE_ENV === "development" ? ".next-dev" : ".next",
  outputFileTracingRoot: __dirname,
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
