// โหลด data/processed/*/*.json เข้า Neon (upsert) แล้วสั่งเว็บล้างแคช (แทน scripts/load_to_neon.py ตาม ADR 0014)
// รัน: npm run load:neon            (โหลดจริง ต้องมี .env)
//      npm run load:neon -- --dry-run (ตรวจไฟล์ด้วย Zod ชุดเดียวกับที่เว็บใช้ ไม่ต่อ DB)
// ค่าจาก .env (env ของเครื่องมาก่อน): DATABASE_URL_DIRECT, REVALIDATE_SECRET, SITE_URL · ไม่พิมพ์ค่าลับออกจอ
// ต่อ DB ด้วย @neondatabase/serverless (HTTP, JavaScript ล้วน) เพราะ psycopg ถูก Application Control ของ Windows บล็อก
import { existsSync, readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

import { neon } from "@neondatabase/serverless";

import { LOADED_DOC_TYPES, storedDocumentSchema, type StoredDocument } from "../lib/contract/stored.ts";

export const REQUIRED_KEYS = ["DATABASE_URL_DIRECT", "REVALIDATE_SECRET", "SITE_URL"] as const;

// รันซ้ำได้ จำนวนแถวไม่เพิ่ม (primary key = doc_type + issue_id) · ไม่มีเวลาประมวลผลในไฟล์ ใส่ loaded_at ตอนโหลด
export const UPSERT = `insert into forecast_issue (issue_id, doc_type, issued_at, source_label, payload)
values ($1, $2, $3, $4, $5::jsonb)
on conflict (doc_type, issue_id) do update set
  issued_at = excluded.issued_at,
  source_label = excluded.source_label,
  payload = excluded.payload,
  loaded_at = now()`;

export type LoadedFile = { file: string; text: string; issue: StoredDocument };
export type FileCheck = { ok: true; value: LoadedFile } | { ok: false; file: string; error: string };

/** อ่าน .env แบบ KEY=VALUE (ข้ามบรรทัดว่าง/คอมเมนต์ ตัดเครื่องหมายคำพูดรอบค่า) */
export function parseEnv(text: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#") || !line.includes("=")) continue;
    const at = line.indexOf("=");
    out[line.slice(0, at).trim()] = line.slice(at + 1).trim().replace(/^(["'])(.*)\1$/, "$2");
  }
  return out;
}

/** ค่าใน env ของเครื่องชนะค่าในไฟล์ (เหมือนสคริปต์ Python เดิม) */
export function mergeEnv(fromFile: Record<string, string>, processEnv: Record<string, string | undefined>) {
  const merged = { ...fromFile };
  for (const key of REQUIRED_KEYS) {
    const value = processEnv[key];
    if (value) merged[key] = value;
  }
  return merged;
}

export function missingKeys(env: Record<string, string>): string[] {
  return REQUIRED_KEYS.filter((key) => !env[key]);
}

/** ไฟล์หนึ่งต้องเป็น JSON ที่ผ่าน Zod ของเว็บ (ตามชนิดใน doc_type) และชื่อไฟล์/โฟลเดอร์ตรงกับ issue_id/doc_type */
export function checkFile(file: string, text: string): FileCheck {
  let data: unknown;
  try {
    data = JSON.parse(text);
  } catch {
    return { ok: false, file, error: "ไม่ใช่ JSON" };
  }
  const parsed = storedDocumentSchema.safeParse(data);
  if (!parsed.success) {
    return { ok: false, file, error: `ไม่ผ่านสัญญา: ${parsed.error.issues[0]?.message ?? "ไม่ทราบสาเหตุ"}` };
  }
  const issue = parsed.data;
  const stem = path.basename(file, ".json");
  const folder = path.basename(path.dirname(file));
  if (stem !== issue.issue_id || folder !== issue.doc_type) {
    return { ok: false, file, error: `ชื่อไฟล์ไม่ตรงกับ ${issue.doc_type}/${issue.issue_id}` };
  }
  return { ok: true, value: { file, text, issue } };
}

/** อ่านทุกไฟล์ใน data/processed/<doc_type>/ เรียงตามชื่อ (ผลซ้ำได้) */
export function readProcessed(dir: string): FileCheck[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .sort()
    .flatMap((docType) =>
      readdirSync(path.join(dir, docType))
        .filter((name) => name.endsWith(".json"))
        .sort()
        .map((name) => {
          const file = path.join(dir, docType, name);
          return checkFile(file, readFileSync(file, "utf-8"));
        }),
    );
}

async function main(argv: string[]): Promise<number> {
  const root = path.resolve(import.meta.dirname, "..");
  const checks = readProcessed(path.join(root, "data", "processed"));
  const bad = checks.filter((c) => !c.ok);
  for (const c of bad) if (!c.ok) console.error(`ไฟล์ไม่ผ่าน: ${path.relative(root, c.file)}: ${c.error}`);
  const good = checks.flatMap((c) => (c.ok ? [c.value] : []));
  const counts = LOADED_DOC_TYPES.map((t) => `${t} ${good.filter((g) => g.issue.doc_type === t).length}`);
  console.log(`files ok: ${good.length} (${counts.join(", ")})`);
  if (bad.length > 0 || good.length === 0) return 2;
  if (argv.includes("--dry-run")) return 0;

  const envFile = path.join(root, ".env");
  const env = mergeEnv(existsSync(envFile) ? parseEnv(readFileSync(envFile, "utf-8")) : {}, process.env);
  const missing = missingKeys(env);
  if (missing.length > 0) {
    console.error(`ขาดค่าใน .env: ${missing.join(", ")} (ดู .env.example)`);
    return 2;
  }

  const sql = neon(env.DATABASE_URL_DIRECT);
  // ทุกไฟล์ในธุรกรรมเดียว: ล้มกลางทางแล้วตารางไม่ค้างครึ่งๆ (เหมือน commit ครั้งเดียวของสคริปต์ Python เดิม)
  await sql.transaction(
    good.map(({ text, issue }) =>
      sql.query(UPSERT, [issue.issue_id, issue.doc_type, issue.issued_at, issue.source_label, text]),
    ),
  );
  const rows = await sql.query(
    "select doc_type, count(*)::int as n from forecast_issue group by doc_type order by doc_type",
  );
  console.log(`rows in forecast_issue: ${rows.map((r) => `${r.doc_type} ${r.n}`).join(", ")}`);

  const res = await fetch(`${env.SITE_URL.replace(/\/+$/, "")}/internal/revalidate`, {
    method: "POST",
    headers: { "x-revalidate-secret": env.REVALIDATE_SECRET },
    signal: AbortSignal.timeout(30_000),
  });
  console.log(`revalidate: HTTP ${res.status}`);
  return res.status === 200 ? 0 : 1;
}

// รันเป็นสคริปต์เท่านั้น (เทสต์นำเข้าฟังก์ชันได้โดยไม่ต่อ DB)
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  // ตั้ง exitCode แทน process.exit(): บน Windows การตัดจบขณะ fetch ยังปิดการเชื่อมต่อทำให้ Node crash (libuv UV_HANDLE_CLOSING)
  main(process.argv.slice(2)).then(
    (code) => {
      process.exitCode = code;
    },
    (err: unknown) => {
      // ข้อความของไดรเวอร์ไม่มีรหัสผ่าน แต่ตัดเหลือบรรทัดแรกกันพิมพ์รายละเอียดการเชื่อมต่อยาวๆ
      console.error(`โหลดไม่สำเร็จ: ${String(err instanceof Error ? err.message : err).split("\n")[0]}`);
      process.exitCode = 1;
    },
  );
}
