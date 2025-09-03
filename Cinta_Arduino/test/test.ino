const int ledRojo = 12;
const int ledVerde = 13;
const int sensor = 10;
const int laser = 9;
const int shutdownButton = 11;
bool active = true;
const int PWM1 = 3;
const int AIN2 = 6;
const int AIN1 = 5;
const int STBY = 7;
const int speed = 230;

void setup() {
  initializePines();
  initialValues();
  detenerMotor();

  Serial.begin(9600);  //initialise serial monitor
  Serial.println("Arduino iniciado");
}

void loop() {
  handleButton();
  if (active == true){
    if (digitalRead(laser) == LOW) {
      digitalWrite(laser, HIGH);
    }
    handleActivationLogic();
  } else {
    stopProgram();
  }
}

void initializePines() {
  pinMode(sensor,INPUT);
  pinMode(ledRojo,OUTPUT);
  pinMode(ledVerde, OUTPUT);
  pinMode(laser, OUTPUT);
  pinMode(shutdownButton, INPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWM1, OUTPUT);
  pinMode(STBY, OUTPUT);
}

void initialValues() {
  digitalWrite(laser, HIGH);
  digitalWrite(ledRojo, LOW);
  digitalWrite(ledVerde, LOW);
}

void handleButton() {
  int buttonState = digitalRead(shutdownButton);
  if (buttonState == LOW) {
    active = !active;
    Serial.println("Cambiando modo del programa a ");
    Serial.println(active ? "Activado" : "Desactivado");
    delay(500);
  }
}

void handleActivationLogic() {
  int temp=digitalRead(sensor);      //assign value of LDR sensor to a temporary variable
  Serial.println(temp);         //send only the value directly

  if(temp==HIGH) {               //HIGH  means,light got blocked
    digitalWrite(ledRojo, HIGH);
    digitalWrite(ledVerde, LOW);
    Serial.println("Encendiendo led rojo");
    detenerMotor();
  } else {
    digitalWrite(ledVerde, HIGH);
    digitalWrite(ledRojo, LOW);
    Serial.println("Encendiendo led verde");       //if light is present,LED off
    girarHorario();
  }
}

void stopProgram() {
  detenerMotor();
  digitalWrite(laser, LOW);
  digitalWrite(ledRojo, LOW);
  digitalWrite(ledVerde, LOW);
}

void girarHorario() {
  Serial.println("Girando en sentido horario");
  digitalWrite(AIN1, HIGH);
  digitalWrite(STBY, HIGH);
  digitalWrite(AIN2, LOW);
  analogWrite(PWM1, speed);
}

void girarAntiHorario() {
  Serial.println("Girando en sentido horario");
  digitalWrite(AIN1, LOW);
  digitalWrite(STBY, HIGH);
  digitalWrite(AIN2, HIGH);
  analogWrite(PWM1, speed);
}

void detenerMotor() {
  Serial.println("Deteniendo motor");
  digitalWrite(AIN1, LOW);
  digitalWrite(STBY, LOW);
  digitalWrite(AIN2, LOW);
  analogWrite(PWM1, 0);
}
