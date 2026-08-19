/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracingRoot: __dirname,
  async rewrites() {
    return [
      {
        source: "/api/collector/:path*",
        destination: `${process.env.CEMS_COLLECTOR_API_BASE || "http://127.0.0.1:8003"}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
