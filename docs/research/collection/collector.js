// ตัวเก็บข้อมูลที่รันในแท็บ www.tmd.go.th ผ่าน Claude in Chrome เท่านั้น (ADR 0015)
// ไม่ใช่สคริปต์บนเครื่อง: ไม่มีอะไรในไฟล์นี้ยิงเว็บเอง ทุกหน้าเปิดในเบราว์เซอร์ของผู้ใช้ทีละหน้า
// วิธีใช้และลำดับขั้น: docs/research/collection-procedure.md
// ฟังก์ชันถูกเก็บเป็นข้อความใน localStorage ("tmdc", "tmdpdf", "tmdstep") แล้วเรียกด้วย (0, eval)

// เก็บข้อความหน้าปัจจุบัน (+ PDF จากปุ่ม "ดาวน์โหลดเอกสาร") ลง IndexedDB "tmdc"
// kind = "__export" ส่งออกทั้งหมดเป็น JSON ไฟล์เดียว (id = ชื่อไฟล์) โดยไม่ล้างที่เก็บ
// kind = "__clear" ล้างที่เก็บ เรียกหลังเห็นไฟล์ใน Downloads แล้วเท่านั้น
// (Chrome อาจบล็อกการดาวน์โหลดอัตโนมัติแบบเงียบ ๆ ถ้าล้างทันทีข้อมูลหายทั้งชุด พบ 2026-11-18)
async function tmdc(kind, id, pdfWanted) {
  const db = await new Promise((res, rej) => { const r = indexedDB.open("tmdc", 1); r.onupgradeneeded = () => r.result.createObjectStore("f"); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); });
  const put = (k, v) => new Promise((res, rej) => { const tx = db.transaction("f", "readwrite"); tx.objectStore("f").put(v, k); tx.oncomplete = res; tx.onerror = () => rej(tx.error); });
  if (kind === "__clear") {
    await new Promise((res) => { const tx = db.transaction("f", "readwrite"); tx.objectStore("f").clear(); tx.oncomplete = res; });
    return "cleared";
  }
  if (kind === "__export") {
    const all = await new Promise((res) => { const out = {}; const tx = db.transaction("f"); const c = tx.objectStore("f").openCursor(); c.onsuccess = () => { const cur = c.result; if (cur) { out[cur.key] = cur.value; cur.continue(); } else res(out); }; });
    const keys = Object.keys(all); if (!keys.length) return "empty";
    const blob = new Blob([JSON.stringify(all)], { type: "application/json" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = id; document.body.appendChild(a); a.click(); a.remove();
    await new Promise(r => setTimeout(r, 1500));
    return "exported " + keys.length + " size " + blob.size + " (not cleared: run __clear after the file is in Downloads)";
  }
  for (let i = 0; i < 20 && document.readyState !== "complete"; i++) await new Promise(r => setTimeout(r, 250));
  // เว้นจังหวะต่อหน้า (ADR 0015)
  await new Promise(r => setTimeout(r, 2000));
  const t = document.body.innerText;
  // จุดเริ่ม/จุดจบของเนื้อหาหลักต่อหมวด (รายวันตรงกับไฟล์เดิมทุกไบต์ ตรวจแล้ว 2026-11-18)
  const M = { daily: ["ลักษณะอากาศทั่วไป", "เนื้อหาในหน้านี้"], shipping: ["ลักษณะอากาศทั่วไป", "เนื้อหาในหน้านี้"], sevenday: ["คาดหมายอากาศทั่วไป", "เนื้อหาในหน้านี้"], warning: ["ประกาศกรมอุตุนิยมวิทยา", "วันที่โพส"], weekly: ["\nประเทศไทย\n", "เนื้อหาในหน้านี้"] }[kind];
  let a = t.indexOf(M[0]); if (kind === "weekly") a += 1;
  // ประกาศเตือนภัยรุ่นเก่า (ก่อน ต.ค. 2569) ไม่มี "วันที่โพส" ใช้ "Tags:" แทน
  const cand = (kind === "warning" ? ["วันที่โพส", "\nTags:"] : [M[1]]).map(m => [t.indexOf(m, a), m.trim()]).filter(x => x[0] >= 0).sort((x, y) => x[0] - y[0]);
  const b = cand.length ? cand[0][0] : -1; const endMark = cand.length ? cand[0][1] : M[1];
  if (a < 0 || b < 0) return "NOMARK " + kind + " " + id;
  const body = t.slice(a, b).replace(/\s+$/, "");
  const sel = document.querySelector("select"); const selOk = !sel || kind === "warning" ? true : sel.options[sel.selectedIndex].value.includes(id);
  const btn = [...document.querySelectorAll("button,a")].find(e => e.textContent.trim() === "ดาวน์โหลดเอกสาร");
  const pdfPath = btn ? ((btn.getAttribute("onclick") || btn.getAttribute("href") || "").match(/\/media\/[^'"]+?\.pdf/) || [""])[0] : "";
  const label = document.title.replace(/^กรมอุตุนิยมวิทยา \| /, "").trim();
  const head = ["# source: " + location.origin + decodeURI(location.pathname), "# round_id: " + id, "# label: " + label, "# pdf: " + pdfPath, "# saved_at: " + new Date().toISOString(), "# note: innerText of page main content, from \"" + M[0].trim() + "\" to before \"" + endMark + "\""].join("\n");
  await put(kind + "/" + kind + "_" + id + ".txt", { text: head + "\n\n" + body, source: location.origin + decodeURI(location.pathname) });
  let pdfInfo = "-";
  if (pdfWanted && pdfPath) {
    const r = await fetch(pdfPath); const buf = new Uint8Array(await r.arrayBuffer());
    if (r.ok && buf[0] === 0x25 && buf[1] === 0x50) { let s = ""; for (let i = 0; i < buf.length; i += 32768) s += String.fromCharCode.apply(null, buf.subarray(i, i + 32768)); await put(kind + "/" + kind + "_" + id + ".pdf", { b64: btoa(s), source: location.origin + pdfPath }); pdfInfo = "pdf " + buf.length; } else pdfInfo = "pdfbad " + r.status;
  }
  return (selOk ? "ok " : "SELMISMATCH ") + kind + " " + id + " len " + body.length + " " + pdfInfo;
}

// หน้าที่มีแต่ PDF (iframe/ปุ่ม/ลิงก์ใต้ /media/) เก็บได้สูงสุด 3 ไฟล์ต่อหน้า
async function tmdpdf(kind, id) {
  for (let i = 0; i < 20 && document.readyState !== "complete"; i++) await new Promise(r => setTimeout(r, 250));
  await new Promise(r => setTimeout(r, 2000));
  const cands = [...document.querySelectorAll("iframe,embed,object,[onclick*='.pdf'],a[href*='.pdf']")].map(e => { const v = decodeURIComponent(e.getAttribute("src") || e.getAttribute("data") || e.getAttribute("onclick") || e.getAttribute("href") || ""); return (v.match(/\/media\/[^'"?#]+?\.pdf/) || [""])[0]; }).filter(Boolean);
  const paths = [...new Set(cands)];
  if (!paths.length) return "NOPDF " + kind + " " + id;
  const db = await new Promise((res, rej) => { const r = indexedDB.open("tmdc", 1); r.onupgradeneeded = () => r.result.createObjectStore("f"); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); });
  const put = (k, v) => new Promise((res, rej) => { const tx = db.transaction("f", "readwrite"); tx.objectStore("f").put(v, k); tx.oncomplete = res; tx.onerror = () => rej(tx.error); });
  const out = [];
  for (let j = 0; j < paths.length && j < 3; j++) {
    const r = await fetch(encodeURI(paths[j])); const buf = new Uint8Array(await r.arrayBuffer());
    if (!(r.ok && buf[0] === 0x25 && buf[1] === 0x50)) { out.push("bad " + r.status); continue; }
    let s = ""; for (let i = 0; i < buf.length; i += 32768) s += String.fromCharCode.apply(null, buf.subarray(i, i + 32768));
    const key = kind + "/" + kind + "_" + id + (j ? "_" + (j + 1) : "") + ".pdf";
    await put(key, { b64: btoa(s), source: location.origin + paths[j], page: location.origin + decodeURI(location.pathname) });
    out.push(buf.length);
    await new Promise(r => setTimeout(r, 1000));
  }
  return "ok " + kind + " " + id + " pdfs " + out.join(",");
}

// หนึ่งขั้นของคิว localStorage "tmdq" = [{kind, id, path, pdf?, pdfonly?}]
// อยู่ผิดหน้า -> ไปหน้าที่ถูก; อยู่หน้าถูก -> เก็บ ลบหัวคิว แล้วไปหน้าถัดไป
async function tmdstep() {
  const q = JSON.parse(localStorage.getItem("tmdq") || "[]");
  if (!q.length) return "done";
  const h = q[0];
  const here = decodeURI(location.pathname).replace(/\/$/, "");
  if (here !== h.path) { location.href = h.path; return "nav " + q.length; }
  const f = (0, eval)("(" + localStorage.getItem(h.pdfonly ? "tmdpdf" : "tmdc") + ")");
  let r;
  try { r = await f(h.kind, h.id, h.pdf); } catch (e) { r = "ERR " + h.kind + " " + h.id + " " + String(e).slice(0, 80); }
  q.shift(); localStorage.setItem("tmdq", JSON.stringify(q));
  const log = JSON.parse(localStorage.getItem("tmdlog") || "[]"); log.push(r); localStorage.setItem("tmdlog", JSON.stringify(log));
  if (q.length) setTimeout(() => { location.href = q[0].path; }, 300);
  return r + " | left " + q.length;
}
