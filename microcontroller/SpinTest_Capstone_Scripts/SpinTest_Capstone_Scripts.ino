int SENS_1_PIN = 27;
int SENS_3_PIN = 32;
int SENS_2_PIN = 33;
int SENS_5_PIN = 2;
int SENS_4_PIN = 4;
int SENS_6_PIN = 15;
int DELAY = 10;


void setup() {

  pinMode(SENS_1_PIN, INPUT);
  pinMode(SENS_3_PIN, INPUT);
  pinMode(SENS_2_PIN, INPUT);
  pinMode(SENS_5_PIN, INPUT);
  pinMode(SENS_4_PIN, INPUT);
  pinMode(SENS_6_PIN, INPUT);


  Serial.begin(9600);
}

void loop() {
 
  int sensed1=analogRead(SENS_1_PIN);
  sensed1=map(sensed1,0,4095,0,3300);

  int sensed2=analogRead(SENS_2_PIN);
  sensed2=map(sensed2,0,4095,0,3300);
  
  int sensed3=analogRead(SENS_3_PIN);
  sensed3=map(sensed3,0,4095,0,3300);
  
  int sensed4=analogRead(SENS_4_PIN);
  sensed4=map(sensed4,0,4095,0,3300);

  int sensed5=analogRead(SENS_5_PIN);
  sensed5=map(sensed5,0,4095,0,3300);

  int sensed6=analogRead(SENS_6_PIN);
  sensed6=map(sensed6,0,4095,0,3300);
  
  Serial.print(sensed1);
  Serial.print(",");
  Serial.print(sensed2);
  Serial.print(",");
  Serial.print(sensed3);
  Serial.print(",");
  Serial.print(sensed4);
  Serial.print(",");
  Serial.print(sensed5);
  Serial.print(",");
  Serial.print(sensed6);
  Serial.println();

  delay(DELAY);
}
