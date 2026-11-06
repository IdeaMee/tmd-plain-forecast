import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const revalidateTag = vi.fn();
vi.mock("next/cache", () => ({ revalidateTag, cacheTag: vi.fn(), cacheLife: vi.fn() }));

const { POST } = await import("./route");
const { secretsMatch } = await import("@/lib/data/revalidate");

function request(secret?: string): Request {
  const headers: Record<string, string> = secret === undefined ? {} : { "x-revalidate-secret": secret };
  return new Request("http://localhost/internal/revalidate", { method: "POST", headers });
}

describe("/internal/revalidate", () => {
  beforeEach(() => {
    vi.stubEnv("REVALIDATE_SECRET", "test-secret-only-for-vitest");
    revalidateTag.mockClear();
  });
  afterEach(() => vi.unstubAllEnvs());

  it("ความลับผิดหรือไม่มี ได้ 401 และไม่ล้างแคช", async () => {
    expect((await POST(request("wrong"))).status).toBe(401);
    expect((await POST(request())).status).toBe(401);
    expect(revalidateTag).not.toHaveBeenCalled();
  });

  it("ความลับถูก ล้างแท็ก forecasts ทันที", async () => {
    const res = await POST(request("test-secret-only-for-vitest"));
    expect(res.status).toBe(200);
    expect(revalidateTag).toHaveBeenCalledWith("forecasts", { expire: 0 });
  });

  it("ยังไม่ตั้ง REVALIDATE_SECRET = ปิดเสมอ", async () => {
    vi.stubEnv("REVALIDATE_SECRET", "");
    expect((await POST(request(""))).status).toBe(401);
    expect(secretsMatch("", "")).toBe(false);
  });
});
