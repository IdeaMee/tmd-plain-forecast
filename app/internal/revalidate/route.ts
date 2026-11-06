// ล้างแคชข้อมูลพยากรณ์หลังสคริปต์โหลดเข้า Neon (scripts/load-to-neon.mts)
// อยู่ใต้ app/internal เพราะ /api/* เป็นของฟังก์ชัน Python
import { revalidateTag } from "next/cache";

import { FORECASTS_TAG } from "@/lib/data/forecasts";
import { isRevalidateAuthorized } from "@/lib/data/revalidate";

export async function POST(request: Request): Promise<Response> {
  if (!isRevalidateAuthorized(request.headers.get("x-revalidate-secret"))) {
    return Response.json({ ok: false }, { status: 401 });
  }
  // มาจากภายนอก (ไม่ใช่ Server Action) จึงหมดอายุทันทีแทน updateTag
  revalidateTag(FORECASTS_TAG, { expire: 0 });
  return Response.json({ ok: true, revalidated: FORECASTS_TAG });
}
