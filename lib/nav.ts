// รายการเมนูชุดเดียวของทั้งเว็บ (Header เดสก์ท็อป/มือถือ และ Footer) · ใส่เฉพาะหน้าที่มีอยู่จริง ห้ามมีลิงก์ 404
// หมวดของรอบ v2 ที่ยังไม่มีหน้า (เตือนภัย, สรุปสภาพอากาศ, เกษตร, คาดหมาย) เพิ่มเมื่อหน้านั้นเสร็จ (แผน 11, 12)
// nav.test.ts ตรวจว่าทุกลิงก์มี app/<route>/page.tsx

export type NavLink = { href: string; label: string; description: string };

export type NavGroup = {
  id: string;
  label: string;
  // คำอธิบายสั้นในเมนูมือถือ
  description: string;
  links: NavLink[];
};

export const NAV_GROUPS: NavGroup[] = [
  {
    id: "forecast",
    label: "พยากรณ์",
    description: "สรุปพยากรณ์ของกรมอุตุนิยมวิทยาแยก 7 ภาค",
    links: [
      { href: "/", label: "รายวัน", description: "ฉบับล่าสุดและย้อนหลัง" },
      { href: "/?type=sevenday", label: "7 วันข้างหน้า", description: "แยกตามช่วงวัน" },
    ],
  },
  {
    id: "knowledge",
    label: "ความรู้",
    description: "ระบบและโมเดลเบื้องหลังเว็บนี้",
    links: [{ href: "/model", label: "โมเดลทำงานอย่างไร", description: "ผลการฝึกและวัดผล" }],
  },
];

// ปุ่มเด่นท้ายเมนู (ปุ่มหลักสีดำ CTA เดียวของ Header)
export const NAV_CTA: NavLink = { href: "/demo", label: "ลองอัปโหลด PDF", description: "สรุปไฟล์ PDF ของกรมเอง" };

/** หมวดนี้เป็นหน้าปัจจุบันไหม (ดูแค่ path เพราะ query ของหน้าแรกเป็นตัวเลือกภายในหน้า) */
export function isGroupCurrent(group: NavGroup, pathname: string): boolean {
  return group.links.some((link) => link.href.split("?")[0] === pathname);
}

/** ทุก path ในเมนู (ใช้ตรวจว่ามีหน้าจริง) */
export function navPaths(): string[] {
  const hrefs = [...NAV_GROUPS.flatMap((g) => g.links.map((l) => l.href)), NAV_CTA.href];
  return [...new Set(hrefs.map((h) => h.split("?")[0]))];
}
