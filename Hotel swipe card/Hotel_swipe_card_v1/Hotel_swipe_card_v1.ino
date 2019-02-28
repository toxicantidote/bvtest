/*
  Hotel swipe card system for BV3/BV5.
  Alex Farrell - September 2018
  
  This system is designed to allow a machine in a hotel to be fitted with a
  door key reader than is used to enable payment systems in the machine when
  presented.
  
  The payment systems remain active until a timer expires, or something
  (presumably a product) passes through the I-vend sensor at the top of the
  collection bin.
  
  If the door is open, the system is overridden and everything is turned on.
  
  Note that this can be used as a partial system - i.e. it can be used only to
  switch MDB, only to switch VPOS, or both. There is no reconfiguration or
  coding needed to achieve this.
*/

// Which digital pin is the relay controlling VPOS power connected to?
#define PIN_RELAY_VPOS 3

// Which digital pin is the relay controlling MDB power connected to?
#define PIN_RELAY_MDB 4

// Which analog pin is the I-vend sensor connected to (active low)
#define PIN_INPUT_IVEND A3

// Which analog pin is the door switch connected to (active low)
#define PIN_INPUT_DOOR A0

// Which analog pin is the hotel swipe card relay connected to (active low)?
#define PIN_INPUT_HOTEL A2

// How long should we wait after the I-vend sensor is tripped to turn off the
// MDB power? You need to allow time for the coin mech to give change. Time in
// milliseconds
#define DELAY_MDB 5000

// How long should we wait after the system has been activated before 
// automatically switching everything off again? Time in milliseconds
#define DELAY_OFF 120000

/* Don't edit below here */
static unsigned long off_time_mdb = 0;
static unsigned long off_time_vpos = 0;

void setup(void);
void loop(void);

void setup() {
  // Configure the output pins
  pinMode(PIN_RELAY_VPOS, OUTPUT);
  pinMode(PIN_RELAY_MDB, OUTPUT);

  pinMode(PIN_INPUT_DOOR, INPUT_PULLUP);
  pinMode(PIN_INPUT_HOTEL, INPUT_PULLUP);
  pinMode(PIN_INPUT_IVEND, INPUT);

  Serial.begin(9600);
}

void loop() {
  /* Basic hysteresys for the door switch. Not pretty, but does the job.
     Ideally we would want to use a pullup here, but we are trying to keep
     the part count as low as possible to simplify the build, as it is being
     made in a poorly equipped (for electronics) workshop. In this case, we
     sample the input a few times to distinguish between noise and something
     (i.e. the door switch) actually pulling the input to ground.
  */
  int dt1 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  int dt2 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  int dt3 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  int dt4 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  int dt5 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  int dt6 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  int dt7 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  int dt8 = analogRead(PIN_INPUT_DOOR);
  int dtavg = (dt1 + dt2 + dt3 + dt4 + dt5 + dt6 + dt7 + dt8) / 8;
  
  // If the door is open, turn everything on
  if (dtavg < 1000) {
    Serial.println("Door open");
    digitalWrite(PIN_RELAY_VPOS, HIGH);
    digitalWrite(PIN_RELAY_MDB, HIGH);
  // If the door is closed, use the normal logic (timer/ivend)
  } else {
    // If the hotel swipe card is activated..
    if (analogRead(PIN_INPUT_HOTEL) < 500) {
      Serial.println("Hotel card activated");
      // Set the timers to turn payment systems off
      off_time_mdb = millis() + DELAY_OFF;
      off_time_vpos = millis() + DELAY_OFF;
      // Turn the payment systems on
      digitalWrite(PIN_RELAY_VPOS, HIGH);
      digitalWrite(PIN_RELAY_MDB, HIGH);
    // If the i-vend sensor is triggered..
    } else if ((analogRead(PIN_INPUT_IVEND) < 500) && (dtavg > 1000)) {
      Serial.println("I-vend triggered");
      /* Set the VPOS to turn off now, and MDB to turn off after a delay (to
         allow the coin mech time to give change)
      */
      off_time_mdb = millis() + DELAY_MDB;
      off_time_vpos = millis();
    }
    
    /* Check the MDB and VPOS off timers (accounting for millis() rollover).
       If the respective timer has expired, turn off that relay.
    */
    if ((long)(millis() - off_time_mdb) >= 0) {
      Serial.println("Time to turn off MDB");
      digitalWrite(PIN_RELAY_MDB, LOW);   
    }
    if ((long)(millis() - off_time_vpos) >= 0) {
      Serial.println("Time to turn off VPOS");
      digitalWrite(PIN_RELAY_VPOS, LOW);    
    }
    
  }
  delay(50);
}
