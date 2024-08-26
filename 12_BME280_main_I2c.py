import time 
import pigpio
import BME280_I2C


s = BME280_I2C.Sensor()

while True:
           
    t, p, h = s.Read_Data()
    print("h={:.2f} p={:.1f} t={:.2f}".format(h, p/100.0, t))
    time.sleep(0.9)

s.Close()