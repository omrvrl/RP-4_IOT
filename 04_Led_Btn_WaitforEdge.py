import pigpio

BTN_PIN = 23

pi = pigpio.pi()

pi.set_mode(BTN_PIN, pigpio.INPUT)
pi.set_pull_up_down(BTN_PIN, pigpio.PUD_UP)

if pi.wait_for_edge(BTN_PIN, pigpio.FALLING_EDGE, 10):
	print("button pressed !")
else:
	print("Time out !")

