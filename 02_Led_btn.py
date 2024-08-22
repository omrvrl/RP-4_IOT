import time
import pigpio

LED_PIN = 17
BTN_PIN = 23

pi = pigpio.pi()

pi.set_mode(LED_PIN, pigpio.OUTPUT)
pi.set_mode(BTN_PIN, pigpio.INPUT)

pi.set_pull_up_down(BTN_PIN, pigpio.PUD_UP)

while True:
    pi.write(LED_PIN, not pi.read(BTN_PIN))
    print(pi.read(BTN_PIN))


