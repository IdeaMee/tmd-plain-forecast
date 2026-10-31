// Vitest สำหรับโค้ดเว็บ (lib/, app/) · server-only ชี้ไปโมดูลว่างแบบเดียวกับที่ Next.js ทำในฝั่งเซิร์ฟเวอร์
import path from "node:path";

import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname),
      "server-only": path.resolve(import.meta.dirname, "node_modules/next/dist/compiled/server-only/empty.js"),
    },
  },
  test: {
    include: ["lib/**/*.test.ts", "app/**/*.test.ts", "scripts/**/*.test.ts"],
    environment: "node",
  },
});
