import type { LineKind } from "@/lib/contract/issue";

// ไอคอนเส้นของชนิดบรรทัดสรุป (ต้นแบบ A) ตกแต่งเท่านั้น ความหมายอยู่ในป้ายข้อความข้างไอคอน
const PATHS: Record<LineKind, string[]> = {
  rain: ["M7 15a4 4 0 0 1-.5-7.97A5.5 5.5 0 0 1 17 8a3.5 3.5 0 0 1 .5 7H7z", "M8 18l-1 2M12 18l-1 2M16 18l-1 2"],
  temperature: ["M10 14.5V5a2 2 0 1 1 4 0v9.5a4 4 0 1 1-4 0z", "M12 9v7"],
  wind: ["M3 8h11a3 3 0 1 0-3-3", "M3 12h16a3 3 0 1 1-3 3", "M3 16h7"],
  wave: ["M2 10c2-2 4-2 6 0s4 2 6 0 4-2 6 0", "M2 15c2-2 4-2 6 0s4 2 6 0 4-2 6 0"],
  fog: ["M4 8h16M2 12h20M4 16h16M7 20h10"],
  other: ["M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z", "M12 11v5M12 8v.5"],
};

export function LineIcon({ kind }: { kind: LineKind }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="size-4.5 shrink-0 text-ink"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {PATHS[kind].map((d) => (
        <path key={d} d={d} />
      ))}
    </svg>
  );
}
