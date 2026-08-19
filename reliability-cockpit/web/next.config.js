/** @type {import('next').NextConfig} */
const nextConfig = {
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