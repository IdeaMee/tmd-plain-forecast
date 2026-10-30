import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: true,
  // ระหว่างที่ Vercel ยังไม่ได้ตั้ง DATABASE_URL หน้า / อ่านไฟล์สำรองใน data/processed (lib/data/forecasts.ts)
  // ต้องรวมไฟล์เหล่านี้เข้าชุด deploy เอง เพราะการอ่านไฟล์ถูกตั้ง turbopackIgnore ไว้ (~1 MB)
  outputFileTracingIncludes: {
    "/": ["./data/processed/**/*.json"],
  },
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
