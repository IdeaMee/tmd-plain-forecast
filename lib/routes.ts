// สร้างลิงก์หน้า / จากตัวเลือก (ชนิดพยากรณ์, ฉบับ, เดือนของตัวเลือกรอบ, ภาค) ค่าเริ่มต้นไม่ใส่ใน URL
import type { RegionKey } from "@/lib/contract/issue";
import { parseMonthParam } from "@/lib/history";

// แท็บของหน้าแรก: รายวัน, 7 วัน, เดินเรือ (11.1)
export const HOME_TYPES = ["daily", "sevenday", "shipping"] as const;
export type HomeType = (typeof HOME_TYPES)[number];

// month = เดือน "YYYY-MM" ที่ตัวเลือกรอบแสดง (ไม่ระบุ = เดือนของฉบับที่เลือก/เดือนล่าสุด)
export type HomeQuery = { type: HomeType; issue: string | null; month: string | null; region: RegionKey | null };

const ISSUE_ID: Record<HomeType, RegExp> = { daily: /^\d{12}$/, sevenday: /^\d{6}$/, shipping: /^\d{12}$/ };

/** พยากรณ์เดินเรือแบ่งตามพื้นที่ทะเล ไม่ใช่ภาค จึงไม่มีตัวเลือกภาค */
export function hasRegions(type: HomeType): boolean {
  return type !== "shipping";
}

export function homeHref({ type, issue, month, region }: HomeQuery): string {
  const params = new URLSearchParams();
  if (type !== "daily") params.set("type", type);
  if (issue) params.set("issue", issue);
  if (month) params.set("month", month);
  if (region && hasRegions(type)) params.set("region", region);
  const query = params.toString();
  return query ? `/?${query}` : "/";
}

function isHomeType(value: unknown): value is HomeType {
  return typeof value === "string" && (HOME_TYPES as readonly string[]).includes(value);
}

/** อ่าน query string แบบไม่เชื่อค่า: ค่าที่ไม่รู้จักหรือรูปแบบผิดใช้ค่าเริ่มต้น */
export function parseHomeQuery(
  raw: Record<string, string | string[] | undefined>,
  isRegion: (v: unknown) => v is RegionKey,
): HomeQuery {
  const type: HomeType = isHomeType(raw.type) ? raw.type : "daily";
  const issue = typeof raw.issue === "string" && ISSUE_ID[type].test(raw.issue) ? raw.issue : null;
  const region = hasRegions(type) && isRegion(raw.region) ? raw.region : null;
  return { type, issue, month: parseMonthParam(raw.month), region };
}
