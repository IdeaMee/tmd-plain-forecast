import "server-only";

import { timingSafeEqual } from "node:crypto";

/** เทียบความลับแบบเวลาคงที่ ความลับว่าง = ไม่อนุญาตเสมอ (ปิดไว้ก่อนถ้ายังไม่ตั้ง env) */
export function secretsMatch(given: string | null, expected: string | undefined): boolean {
  if (!given || !expected) {
    return false;
  }
  const a = Buffer.from(given);
  const b = Buffer.from(expected);
  return a.length === b.length && timingSafeEqual(a, b);
}

export function isRevalidateAuthorized(header: string | null): boolean {
  return secretsMatch(header, process.env.REVALIDATE_SECRET);
}
