
## MDB test (not working)

port = 'COM2'

###
import serial

## Pretend to do 9 bit per MDB by using a parity bit
conn = serial.Serial(port, baudrate=9600, stopbits = serial.STOPBITS_TWO, timeout = 1, write_timeout = 1)

while True:


    data = conn.read(1)
    if (len(str(data)) > 3):
        
        print('Byte received ' + str(len(str(data))) + ': ' + str(data))
        if (str(data) == 'b\'z\''):
            print('sending hello')
            conn.write([0x3B, 0x7B, 0x00])
            conn.flush()
            conn.write([0x00, 0x3D, 0x7D, 0x00, 0xE6, 0x0E, 0x00, 0x06, 0x19, 0x00, 0x3D, 0x7D, 0x00, 0x3D, 0x7D, 0x00, 0xCF, 0x1F, 0x00, 0xCF, 0x1F, 0x00, 0xCF, 0x1F, 0x00, 0xCF, 0x1F, 0x00, 0xCF, 0x1F, 0x00])
            conn.flush()
