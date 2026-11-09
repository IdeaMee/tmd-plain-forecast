import { Container } from "@/components/layout/container";
import { Disclaimer } from "@/components/features/disclaimer";

// footer-light ของ DESIGN-expo (body-sm สี body)
export function Footer() {
  return (
    <footer className="mt-12 border-t border-hairline bg-canvas lg:mt-24">
      <Container className="space-y-2 py-12">
        <Disclaimer />
        <p className="text-body-sm text-body">
          ข้อความสรุปเขียนจากประกาศของกรมอุตุนิยมวิทยาโดยอัตโนมัติ ตัวเลข ชื่อจังหวัด และคำแนะนำคัดจากต้นฉบับ
          ถ้าต้องตัดสินใจเรื่องความปลอดภัย โปรดดูประกาศฉบับเต็มของกรมอุตุนิยมวิทยา
        </p>
        <p className="text-body-sm text-body">โครงงานรายวิชา NLP และ Machine Learning</p>
      </Container>
    </footer>
  );
}
