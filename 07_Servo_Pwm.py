import time
import pigpio

SRV_PIN = 17

pi = pigpio.pi()

while True:

    pi.set_servo_pulsewidth(SRV_PIN,500)
    time.sleep(1)
    pi.set_servo_pulsewidth(SRV_PIN,1000)
    time.sleep(1)
    pi.set_servo_pulsewidth(SRV_PIN,1500)
    time.sleep(1)
    pi.set_servo_pulsewidth(SRV_PIN,2000)
    time.sleep(1)
    pi.set_servo_pulsewidth(SRV_PIN,2500)
    time.sleep(1)
