import time
import pigpio

PWM_PIN = 17

pi = pigpio.pi()

pi.set_PWM_frequency(PWM_PIN,10)
pi.set_PWM_range(PWM_PIN,1000)

pi.set_PWM_dutycycle(PWM_PIN, 250)
time.sleep(1)
pi.set_PWM_dutycycle(PWM_PIN, 750)
time.sleep(1)
pi.set_PWM_dutycycle(PWM_PIN, 500)
time.sleep(1)
pi.set_PWM_dutycycle(PWM_PIN, 0)



