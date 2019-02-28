/*
 * Pin code for products proof of concept
 * Alex Farrell - February 2019
 * 
 * Allows vending of products using a PIN code. Codes are sent as prepaid card
 * numbers to the Nayax system for ease of use and traceability.
 * 
 * Takes over the LCD and keypad to allow entry of a PIN code, which is then sent to
 * the Nayax DTU as a card number.
 * 
 * Built using an Arduino Pro Mini.
 * 
 * Connections:
 *  D2  - Not used
 *  D3  - Not used
 *  D4  - Not used
 *  D5  - Keypad row 1 output relay
 *  D6  - Keypad row 2 output relay
 *  D7  - Keypad row 3 output relay
 *  D8  - Keypad row 4 output relay
 *  D9  - Keypad column 4 output relay
 *  D10 - Keypad column 3 output relay
 *  D11 - Keypad column 2 output relay
 *  D12 - Keypad column 1 output relay
 *  D13 - Not used
 *  A0  - Keypad row 4 input
 *  A1  - Keypad row 3 input
 *  A2  - Output buffer enable pin
 *  A3  - Not used
 *  A4  - LCD I2C SDA
 *  A5  - LCD I2C SCL
 *  A6  - Keypad row 2 input
 *  A7  - Keypad row 1 input
 */
 
 
 /* TODO: Rewrite LCD functions for the new I2C connected LCD interface */
 

// Row output pins (to VMC)
#define ROW_OUT1 5
#define ROW_OUT2 6
#define ROW_OUT3 7
#define ROW_OUT4 8

// Column output pins (to VMC)
#define COL_OUT1 12
#define COL_OUT2 11
#define COL_OUT3 10
#define COL_OUT4 9

// Row input pins (from keypad)
#define ROW_IN1 A7
#define ROW_IN2 A6
#define ROW_IN3 A1
#define ROW_IN4 A0

// LCD interface pins
#define LCD_SDA 2
#define LCD_SCL 4

// Pin that decides whether we have LCD control or the VMC does
#define LCD_CONTROL A2

// Analog input values that correspond to each column of the keypad being pressed
#define LOW_COL4 700
#define HIGH_COL4 800
#define LOW_COL3 500
#define HIGH_COL3 600
#define LOW_COL2 200
#define HIGH_COL2 300
#define LOW_COL1 0
#define HIGH_COL1 100

// How long to hold the button for when passing through keypad presses (in ms)
#define DELAY_PRESS 100

/* NO EDITING BELOW HERE */
#include <LiquidCrystal.h>
//LiquidCrystal lcd(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

byte icon_lock[8] = {
    0b00000,
	0b01110,
	0b01010,
	0b01010,
	0b11111,
	0b11011,
	0b11111,
	0b11111
};

byte icon_hide[8] = {
	0b00000,
	0b00000,
	0b01110,
	0b11111,
	0b11111,
	0b11111,
	0b01110,
	0b00000
};

// State variables
bool control_keypad = false;
bool control_lcd = false;
char pin [5];
short pin_pos = 0;


void resetRelays() {
  digitalWrite(ROW_OUT1, LOW);
  digitalWrite(ROW_OUT2, LOW);
  digitalWrite(ROW_OUT3, LOW);
  digitalWrite(ROW_OUT4, LOW);

  digitalWrite(COL_OUT1, LOW);
  digitalWrite(COL_OUT2, LOW);
  digitalWrite(COL_OUT3, LOW);
  digitalWrite(COL_OUT4, LOW);
}

void send_button(int button) {
  switch(button) {
	case 0:
	  digitalWrite(ROW_OUT4, HIGH);
	  digitalWrite(COL_OUT2, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT4, HIGH);
	  digitalWrite(COL_OUT2, HIGH);
	  break;

	case 1:
	  digitalWrite(ROW_OUT1, HIGH);
	  digitalWrite(COL_OUT1, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT1, HIGH);
	  digitalWrite(COL_OUT1, HIGH);
	  break;
  
	case 2:
	  digitalWrite(ROW_OUT1, HIGH);
	  digitalWrite(COL_OUT2, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT1, HIGH);
	  digitalWrite(COL_OUT2, HIGH);
	  break;
  
	case 3:
	  digitalWrite(ROW_OUT1, HIGH);
	  digitalWrite(COL_OUT3, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT1, HIGH);
	  digitalWrite(COL_OUT3, HIGH);
	  break;
	  
	case 4:
	  digitalWrite(ROW_OUT2, HIGH);
	  digitalWrite(COL_OUT1, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT2, HIGH);
	  digitalWrite(COL_OUT1, HIGH);
	  break;
  
	case 5:    
	  digitalWrite(ROW_OUT2, HIGH);
	  digitalWrite(COL_OUT2, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT2, HIGH);
	  digitalWrite(COL_OUT2, HIGH);
	  break;
  
	case 6:
	  digitalWrite(ROW_OUT2, HIGH);
	  digitalWrite(COL_OUT3, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT2, HIGH);
	  digitalWrite(COL_OUT3, HIGH);
	  break;
  
	case 7:
	  digitalWrite(ROW_OUT3, HIGH);
	  digitalWrite(COL_OUT1, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT3, HIGH);
	  digitalWrite(COL_OUT1, HIGH);
	  break;
  
	case 8:
	  digitalWrite(ROW_OUT3, HIGH);
	  digitalWrite(COL_OUT2, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT3, HIGH);
	  digitalWrite(COL_OUT2, HIGH);
	  break;
  
	case 9:
	  digitalWrite(ROW_OUT3, HIGH);
	  digitalWrite(COL_OUT3, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT3, HIGH);
	  digitalWrite(COL_OUT3, HIGH);
	  break;

	// star
	case 10:
	  digitalWrite(ROW_OUT4, HIGH);
	  digitalWrite(COL_OUT1, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT4, HIGH);
	  digitalWrite(COL_OUT1, HIGH);
	  break;

	// hash
	case 11:
	  digitalWrite(ROW_OUT4, HIGH);
	  digitalWrite(COL_OUT3, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT4, HIGH);
	  digitalWrite(COL_OUT3, HIGH);
	  break;

	// A
	case 12:
	  digitalWrite(ROW_OUT1, HIGH);
	  digitalWrite(COL_OUT4, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT1, HIGH);
	  digitalWrite(COL_OUT4, HIGH);
	  break;
	  
	// B
	case 13:
	  digitalWrite(ROW_OUT2, HIGH);
	  digitalWrite(COL_OUT4, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT2, HIGH);
	  digitalWrite(COL_OUT4, HIGH);
	  break;

	// C
	case 14:
	  digitalWrite(ROW_OUT3, HIGH);
	  digitalWrite(COL_OUT4, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT3, HIGH);
	  digitalWrite(COL_OUT4, HIGH);
	  break;

	// D
	case 15:
	  digitalWrite(ROW_OUT4, HIGH);
	  digitalWrite(COL_OUT4, HIGH);
	  delay(DELAY_PRESS);
	  digitalWrite(ROW_OUT4, HIGH);
	  digitalWrite(COL_OUT4, HIGH);
	  break;

   default:
	  break;
 }
}

int scan_button() {
  int inr1 = analogRead(ROW_IN1);
  int inr2 = analogRead(ROW_IN2);
  int inr3 = analogRead(ROW_IN3);
  int inr4 = analogRead(ROW_IN4);
	
  if ((inr1 >= LOW_COL1) && (inr1 <= HIGH_COL1)) {
	return 1;
  } else if ((inr1 >= LOW_COL2) && (inr1 <= HIGH_COL2)) {
	return 2;
  } else if ((inr1 >= LOW_COL3) && (inr1 <= HIGH_COL3)) {
	return 3;
  } else if ((inr1 >= LOW_COL4) && (inr1 <= HIGH_COL4)) {
	return 12;
  } else if ((inr2 >= LOW_COL1) && (inr2 <= HIGH_COL1)) {
	return 4;
  } else if ((inr2 >= LOW_COL2) && (inr2 <= HIGH_COL2)) {
	return 5;
  } else if ((inr2 >= LOW_COL3) && (inr2 <= HIGH_COL3)) {
	return 6;
  } else if ((inr2 >= LOW_COL4) && (inr2 <= HIGH_COL4)) {
	return 13;
  } else if ((inr3 >= LOW_COL1) && (inr3 <= HIGH_COL1)) {
	return 7;
  } else if ((inr3 >= LOW_COL2) && (inr3 <= HIGH_COL2)) {
	return 8;
  } else if ((inr3 >= LOW_COL3) && (inr3 <= HIGH_COL3)) {
	return 9;
  } else if ((inr3 >= LOW_COL4) && (inr3 <= HIGH_COL4)) {
	return 14;
  } else if ((inr4 >= LOW_COL1) && (inr4 <= HIGH_COL1)) {
	return 10;
  } else if ((inr4 >= LOW_COL2) && (inr4 <= HIGH_COL2)) {
	return 0;
  } else if ((inr4 >= LOW_COL3) && (inr4 <= HIGH_COL3)) {
	return 11;
  } else if ((inr4 >= LOW_COL4) && (inr4 <= HIGH_COL4)) {
	return 15;
  } else {
	return 20;
  }
}

int scan_button_bounce(void) {
  int btn1 = scan_button();
  delay(25);
  int btn2 = scan_button();
  delay(25);
  int btn3 = scan_button();
  if ((btn1 == btn2) && (btn2 == btn3)) {
	return btn1;
  } else {
	return 20;
  }
}

void lcd_take_control(void) {
    // don't bother doing init if we already have control
    if (control_lcd == false) {
        digitalWrite(LCD_CONTROL, HIGH);
        lcd.begin(16, 2);
        lcd.createChar(0, icon_lock);
        lcd.createChar(1, icon_hide);
        lcd.clear();
        control_lcd = true;
    }   
}

void lcd_release_control(void) {
    // allow data through the buffer
    digitalWrite(LCD_CONTROL, LOW); 
    // set back to 8 bit mode
    //lcd.command(3);
    control_lcd = false;
}

void send_pin() {
    clear_pin();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Checking PIN");
    lcd.setCursor(0, 1);
    lcd.print("Please wait...");
    delay(2000);
    // TODO: write code to send pin
}

void clear_pin(void) {
    pin_pos = 0;
}

void prompt_pin(void) {
    control_keypad = true;
    lcd_take_control();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Enter PIN code");
    lcd.setCursor(0, 1);
    lcd.print(" ");
    lcd.write((uint8_t)0);
    lcd.print(" ");
    for (int i = 0; i < pin_pos; i++) {
        lcd.write((uint8_t)1);
    }
} 

void setup() {
  pinMode(ROW_OUT1, OUTPUT);
  pinMode(ROW_OUT2, OUTPUT);
  pinMode(ROW_OUT3, OUTPUT);
  pinMode(ROW_OUT4, OUTPUT);
  pinMode(COL_OUT1, OUTPUT);
  pinMode(COL_OUT2, OUTPUT);
  pinMode(COL_OUT3, OUTPUT);
  pinMode(COL_OUT4, OUTPUT);

  pinMode(ROW_IN1, INPUT_PULLUP);
  pinMode(ROW_IN2, INPUT_PULLUP);
  pinMode(ROW_IN3, INPUT_PULLUP);
  pinMode(ROW_IN4, INPUT_PULLUP);
  
  pinMode(LCD_CONTROL, OUTPUT);
  // give LCD control to the VMC by default
  //lcd_release_control();
  
  resetRelays();
  
  // test - take control
  control_keypad = true;
  lcd_take_control();
  lcd.write((uint8_t)0);
  lcd.print(" PIN system");
  lcd.setCursor(0, 1);
  lcd.print("ready!");
  delay(500);
  }

void loop() {
  resetRelays();
  int btn = scan_button_bounce(); 
  
  
  // send the keypress through if a button was pressed and we are not in control
  if ((btn != 20) && (control_keypad == false)) {
	  send_button(btn);
  } else if (control_keypad == true) {
      if (btn != 20) {
        Serial.println(btn);
        // digits add to pin
        if ((btn >= 0) && (btn <= 9)) {            
            // max 8 digits
            if (pin_pos <= 7) {
                //pin[pin_pos] = btn;
                pin_pos++;                
                prompt_pin();
            }
            
        // hash to enter
        } else if (btn == 11) {
            send_pin();
        // C or hash to clear
        } else if ((btn == 14) || (btn == 10)) {
            clear_pin();
        }
      } else {
          prompt_pin();
      }
  } 
}


