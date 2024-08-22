import time 
import pigpio

pi = pigpio.pi()
h = pi.spi_open(0,50000,0)

while True:
    (count, rx_data) = pi.spi_xfer(h, b"DEEPMAKER")
    print(rx_data)
    time.sleep(1)

pi.spi_close(h)
