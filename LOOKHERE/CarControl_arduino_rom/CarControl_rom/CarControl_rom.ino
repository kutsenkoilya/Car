#include <Servo.h>
#include <Ultrasonic.h>

#define servo_pin 10

#define eng_a 8
#define eng_b 9
#define eng_en 11

int sonic_ports[3][2] = {{2, 3}, {4, 5}, {6, 7}};

Servo servo;

Ultrasonic sonic_r(sonic_ports[0][0], sonic_ports[0][1]);
Ultrasonic sonic_l(sonic_ports[1][0], sonic_ports[1][1]);
Ultrasonic sonic_m(sonic_ports[2][0], sonic_ports[2][1]);

int event = 3;
int val = 0;
int deg = 90;

void setup() {
  Serial.begin(9600);
  
  servo.attach(servo_pin);
  servo.write(90);
  pinMode(eng_a, OUTPUT);
  pinMode(eng_b, OUTPUT);
}

void loop() {  
  if (Serial.available() > 1) {  
    event = (int)Serial.read();

    if (event == 3) {
      deg = (int)Serial.read();
    } else {
      val = (int)Serial.read();
    }
  }

  if (event == 4) {
    Serial.write(0);
    Serial.write(readDistanceSmoothly(sonic_l));
    delay(10);
   
    Serial.write(1);
    Serial.write(readDistanceSmoothly(sonic_m));
    delay(10);
    
    Serial.write(2);
    Serial.write(readDistanceSmoothly(sonic_r));
    delay(10);
    
    event = 256;
  }
    
  analogWrite(eng_en,val); //скорость
  
  servo.write(deg); //поворот
    
  if (event == 0) {
    digitalWrite(eng_a,LOW); //стоп
    digitalWrite(eng_b,LOW);
  }
 
  if (event == 1) {
    digitalWrite(eng_a,HIGH); //вперёд
    digitalWrite(eng_b,LOW);
  }
 
 if (event == 2) {
    digitalWrite(eng_a,LOW); //назад
    digitalWrite(eng_b,HIGH);
  }
}

float readDistanceSmoothly(Ultrasonic s)
{
  float x;
  float prev_val; 
  float delta;
  int counter = 0;
  float sum = 0;
  
  for (int i = 0; i < 5; i++)
  {
    x = s.distanceRead();

    if (x>1000)
    {
      x = 1000;
      }
    
    if (i>0)
    {
      delta = x - prev_val;
      if (delta < 10)
      {
        sum += x;
        counter++;
      }
    }
    else
    {
      sum += x;
      counter++;
    }
    prev_val = x;
    delay(10);
  
  }
  
  return x / counter;
  
  }
