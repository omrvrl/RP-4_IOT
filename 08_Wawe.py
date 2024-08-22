import time 
import pigpio

OUT_PIN = 17

pi = pigpio.pi()

if not pi.connected:
	exit()

pulseList = []

pulseList.append(pigpio.pulse(1<<OUT_PIN,0,100000))
pulseList.append(pigpio.pulse(0,1<<OUT_PIN,500000))
pulseList.append(pigpio.pulse(1<<OUT_PIN,0,250000))
pulseList.append(pigpio.pulse(0,1<<OUT_PIN,500000))
pulseList.append(pigpio.pulse(1<<OUT_PIN,0,500000))
pulseList.append(pigpio.pulse(0,1<<OUT_PIN,500000))
pulseList.append(pigpio.pulse(1<<OUT_PIN,0,750000))
pulseList.append(pigpio.pulse(0,1<<OUT_PIN,500000))

pi.wave_clear()
pi.wave_add_generic(pulseList)
waveId = pi.wave_create()
pi.wave_send_using_mode(waveId, pigpio.WAVE_MODE_REPEAT)

time.sleep(10)
pi.wave_tx_stop()
pi.wave_clear()
