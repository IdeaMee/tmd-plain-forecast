"use client";

import { useEffect } from "react";

import { Container } from "@/components/layout/container";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

type ErrorPageProps = { error: unknown; retry: () => void };

// ผิดพลาดตอนดึงข้อมูล (เช่น ฐานข้อมูลไม่ตอบ หรือข้อมูลไม่ผ่านสัญญา) บอกว่าต้องทำอะไร + ปุ่มลองใหม่
export default function ErrorPage({ error, retry }: ErrorPageProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main>
      <Container className="py-12">
        <Alert tone="warning" role="alert">
          <h1 className="text-title-md">โหลดข้อมูลพยากรณ์ไม่สำเร็จ</h1>
          <p className="mt-1">
            ระบบอ่านข้อมูลไม่ได้ในตอนนี้ ลองใหม่อีกครั้ง ถ้ายังไม่ได้ ดูประกาศฉบับเต็มได้ที่เว็บไซต์กรมอุตุนิยมวิทยา
          </p>
          <Button className="mt-4" onClick={() => retry()}>
            ลองใหม่
          </Button>
        </Alert>
      </Container>
    </main>
  );
}
