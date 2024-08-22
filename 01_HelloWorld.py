import pigpio
import time


PIN_LED=17


pi = pigpio.pi()

pi.set_mode(PIN_LED, pigpio.OUTPUT)

while True:

	pi.write(PIN_LED,1)
	time.sleep(1)
	pi.write(PIN_LED,0)
	time.sleep(1)
