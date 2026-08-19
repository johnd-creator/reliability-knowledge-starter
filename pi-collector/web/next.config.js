/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracingRoot: __dirname,
  async rewrites() {
    return [
      {
        source: "/api/collector/:path*",
        destination: `${process.env.COLLECTOR_API_BASE || "http://127.0.0.1:8001"}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
