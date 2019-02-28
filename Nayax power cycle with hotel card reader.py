import threading
import serial
import time
import random

class serialHandler(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        
        self.connection = serial.serial_for_url(port, baudrate = 9600)
        
    def run(self):
        ## characters waiting
        if self.connection.inWaiting() >= 1:
            try:
                line = self.connection.readline()
                cleanLine = line.decode("utf-8").rstrip('\r\n')
                if cleanLine != '':
                    print('RX: ' + str(line))
            except:
                print('Error reading from serial connection')
                
    def write(self, data):
        if not isinstance(data, bytes):
            data = bytes(data, encoding='utf-8', errors = 'ignore')
        
        try:
            self.connection.write(data)
            self.connection.flush()
        except:
            print('Could not write data to serial port')

class cycleTest(threading.Thread):
    def __init__(self, ser):
        threading.Thread.__init__(self)
        
        self.ser = ser
        
    def run(self):
        count = 1
        while True:
            offwait = random.randint(5, 30)
            print('Running VPOS cycle test #' + str(count) + '...')
            self.ser.write('HOTEL\r\n')
            print('VPOS on. Turning off in ' + str(offwait) + ' seconds..')
            time.sleep(offwait)
            self.ser.write('IVEND\r\n')
            print('VPOS off. Waiting 5 seconds before next test..')
            time.sleep(5)
            count += 1
            
print('Opening serial connection..')
ser = serialHandler('COM6')
print('Starting receiver loop..')
ser.start()
print('Running test..')
test = cycleTest(ser)
test.run()

