import pigpio
import time

HW_PWM_PIN = 18
pi = pigpio.pi()
pi.hardware_PWM(HW_PWM_PIN, 1000, 250000)
time.sleep(1)
pi.hardware_PWM(HW_PWM_PIN, 1000, 500000)
time.sleep(1)
pi.hardware_PWM(HW_PWM_PIN, 1000, 750000)
time.sleep(1)
pi.hardware_PWM(HW_PWM_PIN, 1000, 1000000)
time.sleep(1)
pi.hardware_PWM(HW_PWM_PIN, 0, 0)
