import pigpio

LED_PIN = 17
BTN_PIN = 23

def myCallback(gpio, level, tick):
	pi.write(LED_PIN, not pi.read(LED_PIN))
	print(gpio, level,tick)
	
pi = pigpio.pi()
pi.set_mode(LED_PIN, pigpio.OUTPUT)
pi.set_mode(BTN_PIN, pigpio.INPUT)

pi.set_pull_up_down(BTN_PIN, pigpio.PUD_UP)

pi.set_glitch_filter(BTN_PIN,10000)
pi.callback(BTN_PIN, pigpio.FALLING_EDGE, myCallback)

while True:
	pass
