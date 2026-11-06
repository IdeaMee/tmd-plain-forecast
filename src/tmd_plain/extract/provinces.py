"""จังหวัด -> ภาค จากข้อมูลจริงในบล็อกภาค (region-scope-map.md หัวข้อ 4)."""

from __future__ import annotations

import re

from tmd_plain.contract import RegionKey

PROVINCES: dict[str, RegionKey] = {
    **dict.fromkeys(
        "เชียงราย เชียงใหม่ แม่ฮ่องสอน ลำพูน ลำปาง แพร่ น่าน พะเยา ตาก สุโขทัย อุตรดิตถ์ "
        "พิษณุโลก พิจิตร เพชรบูรณ์ กำแพงเพชร".split(),
        "north",
    ),
    **dict.fromkeys(
        "เลย หนองคาย หนองบัวลำภู บึงกาฬ อุดรธานี สกลนคร นครพนม มุกดาหาร กาฬสินธุ์ ขอนแก่น "
        "มหาสารคาม ร้อยเอ็ด ยโสธร อำนาจเจริญ อุบลราชธานี ศรีสะเกษ สุรินทร์ บุรีรัมย์ ชัยภูมิ "
        "นครราชสีมา".split(),
        "northeast",
    ),
    **dict.fromkeys(
        "อุทัยธานี ชัยนาท นครสวรรค์ ลพบุรี สิงห์บุรี อ่างทอง พระนครศรีอยุธยา สระบุรี สุพรรณบุรี "
        "นครปฐม สมุทรสาคร สมุทรสงคราม ราชบุรี กาญจนบุรี".split(),
        "central",
    ),
    **dict.fromkeys("นครนายก ปราจีนบุรี สระแก้ว ฉะเชิงเทรา ชลบุรี ระยอง จันทบุรี ตราด".split(), "east"),
    **dict.fromkeys(
        "เพชรบุรี ประจวบคีรีขันธ์ ชุมพร สุราษฎร์ธานี นครศรีธรรมราช พัทลุง สงขลา ปัตตานี ยะลา นราธิวาส".split(),
        "south_east_coast",
    ),
    **dict.fromkeys("ระนอง พังงา ภูเก็ต กระบี่ ตรัง สตูล".split(), "south_west_coast"),
    # ปริมณฑล 3 จังหวัดไม่เคยพบในบล็อก แมปเป็นกรุงเทพฯ ตามข้อเสนอในสเปก [unverified]
    **dict.fromkeys("กรุงเทพมหานคร นนทบุรี ปทุมธานี สมุทรปราการ".split(), "bangkok_vicinity"),
}

# สะกดผิดที่พบจริงในต้นฉบับ (ฏ แทน ฎ) -> ชื่อที่ถูก
ALIASES: dict[str, str] = {"สุราษฏร์ธานี": "สุราษฎร์ธานี"}

# ชื่อยาวก่อน เพื่อไม่ให้ชื่อสั้นจับส่วนของชื่อยาว
PROVINCE_RE = re.compile(
    "|".join(re.escape(n) for n in sorted([*PROVINCES, *ALIASES], key=len, reverse=True))
)


def canonical(name: str) -> str:
    return ALIASES.get(name, name)


def province_region(name: str) -> RegionKey:
    return PROVINCES[canonical(name)]
