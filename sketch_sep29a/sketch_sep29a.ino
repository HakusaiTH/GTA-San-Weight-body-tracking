#include <Servo.h>
Servo myservo; // ประกาศตัวแปรแทน Servo

void setup() {
  Serial.begin(9600);  // เปิด Serial
  myservo.attach(D4);  // กำหนดขา D4 ควบคุม Servo
}

void loop() {
  if (Serial.available() > 0) {  // ตรวจสอบว่ามีข้อมูลเข้ามาทาง Serial
    char data = Serial.read();  // อ่านข้อมูลจาก Serial
    if (data == '1') {  // ถ้าได้รับ '1' หมุน Servo ไปที่ 180 องศาแล้วกลับที่ 0
      myservo.write(180);  // หมุน Servo ไปที่ 180 องศา
      delay(1000);  // หน่วงเวลา 1000ms
      myservo.write(0);  // หมุน Servo กลับไปที่ 0 องศา
      delay(1000);  // หน่วงเวลา 1000ms
    }
  }
}
