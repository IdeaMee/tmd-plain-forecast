import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // ค่าเริ่มต้นของ eslint-config-next + โฟลเดอร์ที่ไม่ใช่โค้ดเว็บ (ราก repo มีเอกสาร ข้อมูล และ Python ปนอยู่)
  globalIgnores([
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    ".venv/**",
    "data/**",
    "course/**",
    "docs/**",
    "ai/**",
  ]),
]);

export default eslintConfig;
