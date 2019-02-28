## Nayax Marshall test

port = 'COM3'

###
import serial
import time

## Pretend to do 9 bit per MDB by using a parity bit
conn = serial.Serial(port, baudrate=115200, parity = serial.PARITY_NONE, timeout = 1, write_timeout = 1)

while True:
    data = conn.read(1)
    print(str(time.time()) + ' RX: ' + str(data))
