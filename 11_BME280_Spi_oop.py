import time
import pigpio
import BME280

pi = pigpio.pi()

s = BME280.sensor(pi=pi, interface=1)

while True:
    h,p,t = s.read_data()
    print("h={:.2f} p={:.1f} t={:.2f}".format(h,p/100.0,t))
    time.sleep(0.9)