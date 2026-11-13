// smoke test ของเว็บจริงหลัง deploy (Phase 6.1, vercel-deploy-checklist ส่วนที่ 4): npm run smoke
// ไม่เปิดเซิร์ฟเวอร์เอง ยิงไปที่ SMOKE_URL (ค่าเริ่มต้นเว็บ production) ใช้ Edge ที่ติดตั้งในเครื่อง
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests/smoke",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 90_000,
  reporter: "list",
  use: {
    channel: "msedge",
    locale: "th-TH",
    baseURL: process.env.SMOKE_URL ?? "https://tmd-plain-forecast.vercel.app",
  },
});
