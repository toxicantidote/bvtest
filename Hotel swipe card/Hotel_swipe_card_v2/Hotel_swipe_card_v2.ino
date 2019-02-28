/*
  Hotel swipe card system for BV3/BV5. Version 2
  Alex Farrell - January 2019
  
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

  ***

  This version is made for the second version of the system, made with parts
  from Element14. Compared to the previous system, the pin wiring is slightly
  different and status LEDs have been added. For this build Arduino Pro Minis
  were used instead of the Freetronics copy.

  Code wise, there is now a serial command interface and configurable
  timeouts.

  There are also some optimisations in data types to try and save RAM. Most
  variables have been changed to the smallest possible type, and serial
  strings have been wrapped with the FString macro so that they reside in
  PROGMEM instead of RAM. A code watchdog was also added.
*/

// Which digital pin is the relay controlling VPOS power connected to?
#define PIN_RELAY_VPOS 2

// Which digital pin is the relay controlling MDB power connected to?
#define PIN_RELAY_MDB 3

// Which digital pin is the external status LED connected to?
#define PIN_LED_EXT 11

// Which digital pin is the internal status LED connected to (usually 13)?
#define PIN_LED_INT 13

// Which analog pin is the I-vend sensor connected to (active low)
#define PIN_INPUT_IVEND A1

// Which analog pin is the door switch connected to (active low)
#define PIN_INPUT_DOOR A2

// Which analog pin is the hotel swipe card relay connected to (active low)?
#define PIN_INPUT_HOTEL A0

// What is the analog input threshold to consider the door open? Values below
// this are considered open. Test in-circuit as the top board has bias.
#define THRESHOLD_DOOR 200

// Similar to above. What is the threshold for the Ivend sensor input?
#define THRESHOLD_IVEND 100

// And again, but for the hotel swipe card input.
#define THRESHOLD_HOTEL 500

// What should we show for the prompt on the serial interface?
#define CMDPROMPT "Hotel card v2> "

/* Don't edit below here */
#include <EEPROM.h>
#include <stdlib.h>
#include <avr/wdt.h>

// cmd line state vars
char cmdBuffer[32];
unsigned short int cmdBufferPosition = 0;
char cmdByte;
bool cmdStatus = false;

// globals
static unsigned long off_time_mdb = 0;
static unsigned long off_time_vpos = 0;
bool door_override = false;
unsigned int DELAY_OFF = 12;
unsigned int DELAY_MDB = 5;
bool state_mdb = false;
bool state_vpos = false;

// cmd buffers
char command[32];
char argument[32];

// initialise functions
void handleCommand(char*);
void showHelp(void);
void resetBuffers(void);
unsigned short int doorState(void);
void power_mdb(bool);
void power_vpos(bool);
void event_hotel(void);
void event_ivend(void);
void serialInterface(void);
void setup(void);
void loop(void);

void setup() {
  // Set watchdog to reset after 1sec
  wdt_enable(WDTO_1S);
  
  // Configure the output pins
  pinMode(PIN_RELAY_VPOS, OUTPUT);
  pinMode(PIN_RELAY_MDB, OUTPUT);

  pinMode(PIN_LED_INT, OUTPUT);
  pinMode(PIN_LED_EXT, OUTPUT);

  pinMode(PIN_INPUT_DOOR, INPUT_PULLUP);
  pinMode(PIN_INPUT_HOTEL, INPUT_PULLUP);
  pinMode(PIN_INPUT_IVEND, INPUT_PULLUP);

  // Set the initial state
  power_vpos(false);
  power_mdb(false);

  digitalWrite(PIN_LED_INT, LOW);
  digitalWrite(PIN_LED_EXT, LOW);

  // Read the configuration
  DELAY_OFF = EEPROM.read(0);  
  DELAY_MDB = EEPROM.read(1);
  
  Serial.begin(9600);
  Serial.println(F(""));
  Serial.println(F("Hotel card system - v2 (Jan 2019)"));
  Serial.print(F("TIMEOUT set at "));
  Serial.print(DELAY_OFF);
  int mult = DELAY_OFF * 10;
  Serial.print(F(" ("));
  Serial.print(mult);
  Serial.print(F(" seconds), MDB extra time set at "));
  Serial.print(DELAY_MDB);
  Serial.println(F(" seconds"));
  Serial.println(F("Enter HELP for command help"));  

  for (unsigned char i = 0; i < 5; i++) {
    digitalWrite(PIN_LED_EXT, HIGH);
    delay(50);
    digitalWrite(PIN_LED_EXT, LOW);
    delay(20);
  }
}

void loop() {
  serialInterface();
        
  // If the door is open (and override disabled), turn everything on
  if (doorState() < THRESHOLD_DOOR) {
    power_vpos(true);
    power_mdb(true);
    digitalWrite(PIN_LED_INT, HIGH);
  // If the door is closed, use the normal logic (timer/ivend)
  } else {
    // If the hotel swipe card is activated..
    if (analogRead(PIN_INPUT_HOTEL) < THRESHOLD_HOTEL) {
      event_hotel();
    // If the i-vend sensor is triggered (and MDB is on)
    } else if ((analogRead(PIN_INPUT_IVEND) < THRESHOLD_IVEND) && (doorState() > THRESHOLD_DOOR) && (state_mdb == true)) {
      event_ivend();
    }
  }

  if (doorState() > THRESHOLD_DOOR) {
    /* Check the MDB and VPOS off timers (accounting for millis() rollover).
       If the respective timer has expired, turn off that relay.
    */
    long remain_mdb = off_time_mdb - millis();
    long remain_vpos = off_time_vpos - millis();
    if ((remain_mdb <= 0) && (state_mdb == true)) {
      Serial.println(F("Time to turn off MDB"));
      power_mdb(false);
      digitalWrite(PIN_LED_EXT, LOW);
      digitalWrite(PIN_LED_INT, LOW);   
    }
    if ((remain_vpos <= 0) && (state_vpos == true)) {
      Serial.println(F("Time to turn off VPOS"));
      power_vpos(false);
      digitalWrite(PIN_LED_EXT, LOW);
      digitalWrite(PIN_LED_INT, LOW);     
    }
  
    // Flash the status LED quickly if the timer is about to expire on either
    if (((remain_mdb < 5000) && (state_mdb == true)) || ((remain_vpos < 5000) && (state_vpos == true))) {
          digitalWrite(PIN_LED_EXT, HIGH);
          delay(50);
          digitalWrite(PIN_LED_EXT, LOW);
          delay(20);
    }
  }

  // Reset the watchdog
  wdt_reset();
}

// serial interface processing
void serialInterface(void) {
  // serial command stuff
  for (unsigned short int i = 0; i < Serial.available() && cmdStatus == false; i++) { // if serial data is available to read
    cmdStatus = false;
    cmdByte = Serial.read(); // read it
    if (cmdByte == 0x0A || cmdByte == 0x0D) { // newline and carriage return
      Serial.flush(); // clear the input buffer
      if (cmdBufferPosition == 0) { // if command is blank
        resetBuffers(); // reset buffers
      } else { // if the command is not blank
        cmdStatus = true; // flag the command as 'ready for processing'
      }
    } else if (cmdByte == 0x7F) { // backspace
      if (cmdBufferPosition != 0) { // don't backspace further than the prompt
      cmdBufferPosition--;
      // backspace on the client
      Serial.print('\b');
      }
    } else { // other char, add to buffer
     // restrict to printable characters
     if ((cmdByte >= 0x20) && (cmdByte <= 0x7E)) {
       cmdBuffer[cmdBufferPosition] = cmdByte; // append to buffer
       cmdBufferPosition++; // increment buffer position
    
        // echo the character back to the client
        Serial.print(cmdByte);
    
      }
    }
  }
  
  if (cmdStatus == true) { // cmd received, but not processed
  
    // in case of backspace, truncate command buffer
    for (unsigned short int i = cmdBufferPosition; i <= strlen(cmdBuffer); i++) {
      cmdBuffer[i] = NULL;
    }
  
    handleCommand(cmdBuffer); // process the command
    resetBuffers(); // clear the command buffers
  }
}

// triggered when a hotel card is presented (or simulated)
void event_hotel(void) {  
  // Set the timers to turn payment systems off. need to cast types for operands to ensure correct arithmetic
  off_time_vpos = millis() + (DELAY_OFF * (long)10000);
  off_time_mdb = off_time_vpos + (DELAY_MDB * (long)1000);

  Serial.println(F("Hotel card activated"));
  
  // Turn the payment systems on
  power_vpos(true);
  power_mdb(true);
  digitalWrite(PIN_LED_INT, HIGH);
}

// triggered when ivend is tripped
void event_ivend(void) {
  Serial.println(F("I-vend triggered"));
  /* Set the VPOS to turn off now, and MDB to turn off after a delay (to
     allow the coin mech time to give change)
  */      
  off_time_vpos = millis();
  off_time_mdb = off_time_vpos + (DELAY_MDB * 1000);
  // Flash the external status led quickly when ivend triggered
  for (int a = 0; a < 3; a++) {
    digitalWrite(PIN_LED_EXT, HIGH);
    delay(50);
    digitalWrite(PIN_LED_EXT, LOW);
    delay(20);
  }
}

// reads door state with hysteresis
unsigned short int doorState(void) {

  if (door_override == true) {
      return 888;
  }
  
  unsigned short int  dt1 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  unsigned short int  dt2 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  unsigned short int  dt3 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  unsigned short int  dt4 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  unsigned short int  dt5 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  unsigned short int  dt6 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  unsigned short int  dt7 = analogRead(PIN_INPUT_DOOR);
  delay(10);
  unsigned short int  dt8 = analogRead(PIN_INPUT_DOOR);
  unsigned short int  dtavg = (dt1 + dt2 + dt3 + dt4 + dt5 + dt6 + dt7 + dt8) / 8;

  return dtavg;
}

// serial command interpreter
void handleCommand(char* cmdBuffer) { // handles commands
  
  // init vars
  char *command = NULL;
  char *argument = NULL;

  char *buf = cmdBuffer;
  
  command = strtok(buf, " "); // first word (command, before space)
  argument = strtok(NULL, " "); // second word (argument, after space)  
  Serial.println(F("")); // newline
  
  // process command
  if (strcasecmp(command, "HELP") == 0) {
    showHelp();    
  } else if (strcasecmp(command, "DOOR") == 0) {
    if (strcasecmp(argument, "CLOSED") == 0) {      
      door_override = true;
      Serial.println(F("Door override enabled (closed door)"));
    } else if (strcasecmp(argument, "OPEN") == 0) {
      door_override = false;
      Serial.println(F("Door override disabled (open door)"));
    } else {
      Serial.println(F("Unknown state, must be CLOSED or OPEN"));
    }   
  } else if (strcasecmp(command, "STATUS") == 0) {
      Serial.println(F("Sensor status:"));
      Serial.print(F("\t("));
      Serial.print(doorState());
      Serial.print(F(") Door "));
      if (door_override == true) {
          Serial.println(F("closed (OVERRIDE)"));
      } else if (doorState() < THRESHOLD_DOOR) {
          Serial.println(F("open"));
      } else {
          Serial.println(F("closed"));          
      }
      Serial.print(F("\t("));
      Serial.print(analogRead(PIN_INPUT_HOTEL));
      Serial.print(F(") Hotel card input "));
      if (analogRead(PIN_INPUT_HOTEL) < THRESHOLD_HOTEL) {
          Serial.println(F("active"));
      } else {
          Serial.println(F("inactive"));
      }
      Serial.print(F("\t("));
      Serial.print(analogRead(PIN_INPUT_IVEND));
      Serial.print(F(") Vend sensor "));
      if (analogRead(PIN_INPUT_IVEND) < THRESHOLD_IVEND) {
          Serial.println(F("blocked"));
      } else {
          Serial.println(F("clear"));
      }
      long remain_mdb = off_time_mdb - millis();
      long remain_vpos = off_time_vpos - millis();
      if (state_mdb == false) {
          Serial.println(F("\tMDB power off"));
      } else {
          Serial.println(F("\tMDB power on"));
          if (doorState() < THRESHOLD_DOOR) {
            Serial.println(F("\t\tTimer disabled - door open"));            
          } else {
            Serial.print(F("\t\tTurning off in "));
            Serial.print(remain_mdb);
            Serial.println(F("ms"));
          }
      }
      if (state_vpos == false) {
          Serial.println(F("\tVPOS power off"));
      } else {
          Serial.println(F("\tVPOS power on"));
          if (doorState() < THRESHOLD_DOOR) {
            Serial.println(F("\t\tTimer disabled - door open"));            
          } else {
            Serial.print(F("\t\tTurning off in "));
            Serial.print(remain_vpos);
            Serial.println(F("ms"));
          }
      }
  } else if (strcasecmp(command, "TIMEOUT") == 0) {
    /* We use strtol instead of atoi here as atoi has 'undefined' behaviour when out of range.
     *  Sounds like a stack smashing risk to me.
     */
    char *tempv;    
    long int tov = strtol(argument, &tempv, 10);
    if ((tov < 255) && (tov > 0)) {      
      unsigned short int result = (tov * 10);
      // recast as int to store as one byte
      int tovs = tov;
      EEPROM.write(0, tovs);
      Serial.print(F("Set timeout to "));
      Serial.print(tovs);
      Serial.print(F(" ("));
      Serial.print(result);
      Serial.print(F(" seconds). Restart to apply setting."));
    } else {
      Serial.println(F("Invalid argument. Multiplier must be a number between 1 and 254"));
    }

  } else if (strcasecmp(command, "CHANGETIME") == 0) {
    char *tempm;
    long int tom = strtol(argument, &tempm, 10);
    if ((tom < 255) && (tom > 0)) {
      int toms = tom;
      EEPROM.write(1, toms);
      Serial.print(F("Set MDB extra time to "));
      Serial.print(toms);
      Serial.print(F(" seconds. Restart to apply setting."));
    } else {
      Serial.println(F("Invalid argument. Must be a number between 1 and 254"));
    }
  } else if (strcasecmp(command, "READ") == 0) {
    Serial.print(F("Selection timeout: "));
    unsigned short int tos = (EEPROM.read(0) * 10);
    Serial.print(tos);
    Serial.println(F(" seconds"));

    Serial.print(F("MDB extra time: "));
    unsigned char tom = EEPROM.read(1);
    Serial.print(tom);
    Serial.println(F(" seconds"));
  } else if (strcasecmp(command, "HOTEL") == 0) {
    event_hotel();
  } else if (strcasecmp(command, "IVEND") == 0) {
    event_ivend();
  } else {
    Serial.println(F("Unknown command. Enter HELP for command help"));
  }
}

void power_mdb(bool state) {
    if (state == true) {
      digitalWrite(PIN_RELAY_MDB, HIGH);      
    } else {
      digitalWrite(PIN_RELAY_MDB, LOW);
    }
    state_mdb = state;
}

void power_vpos(bool state) {
    if (state == true) {
      digitalWrite(PIN_RELAY_VPOS, HIGH);      
    } else {
      digitalWrite(PIN_RELAY_VPOS, LOW);
    }  
    state_vpos = state;
}

// print help information
void showHelp() {
  // need to do a few watchdog resets in here in case of slow serial
  wdt_reset();
  Serial.println(F("#############################"));
  Serial.println(F("## Hotel swipe card system ##"));
  Serial.println(F("#############################"));

  Serial.println(F("Version 2 - January 2019"));
  Serial.println(F("Developed by Alex Farrell for Benleigh Vending Systems"));
  Serial.println(F("Command arguments are cAsE sensitive"));
  
  Serial.println(F("\nGeneral commands:"));
  Serial.println(F("\t                HELP - Show this help"));  

  // need to do a few watchdog resets in here in case of slow serial
  wdt_reset();
  Serial.println(F("\nConfiguration:"));
  Serial.println(F("\tTIMEOUT <multiplier> - Set the timeout for purchase as multiples of ten"));
  Serial.println(F("\t                       seconds. e.g. a value of 5: 5x10 = 50 sec"));
  Serial.println(F("\tCHANGETIME <seconds> - Set the extra number of seconds to keep the cash"));
  Serial.println(F("\t                       devices on (after I-vend or timeout is triggered)"));
  Serial.println(F("\t                       to allow time to give change"));
  Serial.println(F("\t                READ - Print out the current setting values"));

  Serial.println(F("\nTest commands:"));
  Serial.println(F("\t  DOOR <CLOSED/OPEN> - Override the door switch state (only affects this module,"));
  Serial.println(F("\t                       not the whole machine)"));
  Serial.println(F("\t               HOTEL - Simulate a hotel card swipe"));
  Serial.println(F("\t               IVEND - Simulate something passing through the I-vend (only affects"));
  Serial.println(F("\t                       this module, not the whole machine)"));
  Serial.println(F("\t              STATUS - Print the current sensor status"));
  // need to do a few watchdog resets in here in case of slow serial
  wdt_reset();
}

// reset the serial command buffers
void resetBuffers() { // resets command buffers and command state
  cmdStatus = false; // reset the processing state
  cmdBufferPosition = 0; // reset the buffer position
  for (unsigned char x = 0; x < 32; x++) { // clear the buffer
    cmdBuffer[x] = NULL; // command buffer
    command[x] = NULL; // command
    argument[x] = NULL; // command arguments
  }
  Serial.println(F(""));
  Serial.print(CMDPROMPT);
}
