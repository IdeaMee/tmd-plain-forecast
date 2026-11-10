// e2e ของหน้า / บน next start (ต้อง build ก่อน: npm run e2e ทำให้) ใช้ Edge ที่ติดตั้งในเครื่อง ไม่ดาวน์โหลดเบราว์เซอร์
// 3 เซิร์ฟเวอร์: ข้อมูลจริงใน data/processed, ข้อมูลว่าง, ข้อมูลเสีย (FORECAST_DATA_DIR)
import path from "node:path";

import { defineConfig } from "@playwright/test";

// รันจากรากโปรเจกต์เสมอ (npm run e2e)
const fixtures = path.resolve("tests/e2e/fixtures");
const server = (port: number, dataDir?: string) => ({
  command: `node node_modules/next/dist/bin/next start -p ${port}`,
  url: `http://localhost:${port}`,
  reuseExistingServer: false,
  timeout: 120_000,
  env: {
    NEXT_TELEMETRY_DISABLED: "1",
    // ไม่ต่อฐานข้อมูลจริงในเทสต์
    DATABASE_URL: "",
    ...(dataDir ? { FORECAST_DATA_DIR: dataDir } : {}),
  },
});

export default defineConfig({
  testDir: "tests/e2e",
  fullyParallel: false,
  workers: 1,
  reporter: "list",
  use: { channel: "msedge", locale: "th-TH" },
  webServer: [server(3100), server(3101, path.join(fixtures, "empty")), server(3102, path.join(fixtures, "broken"))],
  projects: [
    { name: "home", testMatch: "home.spec.ts", use: { baseURL: "http://localhost:3100" } },
    { name: "demo", testMatch: "demo.spec.ts", use: { baseURL: "http://localhost:3100" } },
    { name: "empty", testMatch: "empty.spec.ts", use: { baseURL: "http://localhost:3101" } },
    { name: "error", testMatch: "error.spec.ts", use: { baseURL: "http://localhost:3102" } },
  ],
});
