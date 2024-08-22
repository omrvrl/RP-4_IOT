import time 
import pigpio

IDR_ADDR = 0xD0
CALIB00_ADDR = 0x88
CALIB26_ADDR = 0xE1
PRESS_MSB_ADDR = 0xF7
CTRL_MEAS_ADDR = 0xF4
CTRL_HUM_ADDR = 0xF2

def compensate_T(adc_T):
	var1 = (adc_T/16384.0 - dig_T1/1024.0) * float(dig_T2)
	var2 = (((adc_T)/131072.0 - (dig_T1)/8192.0) *
    	   ((adc_T)/131072.0 - (dig_T1)/8192.0)) * (dig_T3)
                         
	t_fine = var1 + var2
                                
	Temp_C = (var1 + var2) / 5120.0
	return (t_fine, Temp_C)

def compensate_P(adc_P):
	var1 = (t_fine/2.0) - 64000.0
	var2 = var1 * var1 * dig_P6 / 32768.0
	var2 = var2 + (var1 * dig_P5 * 2.0)
	var2 = (var2/4.0)+(dig_P4 * 65536.0)
	var1 = ((dig_P3 * var1 * var1 / 524288.0) + (dig_P2 * var1)) / 524288.0
	var1 = (1.0 + var1 / 32768.0)*dig_P1
	
	if var1 == 0.0:
		return 0
		
	p = 1048576.0 - adc_P
	p = (p - (var2 / 4096.0)) * 6250.0 / var1
	var1 = dig_P9 * p * p / 2147483648.0
	var2 = p * dig_P8 / 32768.0
	p = p + (var1 + var2 + dig_P7) / 16.0
	return p    

def compensate_H(adc_H):
	h = t_fine - 76800.0	
	h = ((adc_H - ((dig_H4) * 64.0 + (dig_H5) / 16384.0 * h)) *
		((dig_H2) / 65536.0 * (1.0 + (dig_H6) / 67108864.0 * h *
		(1.0 + (dig_H3) / 67108864.0 * h))))
	h = h * (1.0 - dig_H1 * h / 524288.0)
	
	if h > 100.0:
		h = 100.0
	elif h < 0.0:
		h = 0.0
	return h

def writeRegs(regDataList):
    for i in range(0, len(regDataList),2):
        regDataList[i] &= ~(0x80)
    pi.spi_xfer(h, regDataList)
 


def readRegs(regAddr, cnt):
    (_, data) = pi.spi_xfer(h, [regAddr | 0x80] + [0] * cnt)
    return list(data[1:])

def make_U16(byte1, byte2):
    return byte1 | (byte2 << 8)

def make_S16(byte1, byte2):
    retval = make_U16(byte1, byte2)
    if retval > 32767:
        retval -= 65536
    return retval

def make_S8(byte):
    if byte > 127:
        byte -= 256
    return byte


pi = pigpio.pi()

h = pi.spi_open(0, 50000,0)

print("ID={}".format(readRegs(IDR_ADDR, 1)))

calib_0_25 = readRegs(CALIB00_ADDR,26)
calib_26_41 = readRegs(CALIB26_ADDR, 16)

calib = calib_0_25 + calib_26_41

for i in range(len(calib)):
    print("calib{} = {}".format(i, calib[i]))

dig_T1 = make_U16(calib[0], calib[1])
dig_T2 = make_S16(calib[2], calib[3])
dig_T3 = make_S16(calib[4], calib[5])
dig_P1 = make_U16(calib[6], calib[7])
dig_P2 = make_S16(calib[8], calib[9])
dig_P3 = make_S16(calib[10], calib[11])
dig_P4 = make_S16(calib[12], calib[13])
dig_P5 = make_S16(calib[14], calib[15])
dig_P6 = make_S16(calib[16], calib[17])
dig_P7 = make_S16(calib[18], calib[19])
dig_P8 = make_S16(calib[20], calib[21])
dig_P9 = make_S16(calib[22], calib[23])
dig_H1 = calib[25]
dig_H2 = make_S16(calib[26], calib[27])
dig_H3 = calib[28]
dig_H4 = (calib[29] << 4) | (calib[30] & 0x0F)
if dig_H4 > 2047:
    dig_H4 -= 4096
dig_H5 = (calib[30] >> 4) | (calib[31] << 4)
if dig_H5 > 2047:
    dig_H5 -= 4096
dig_H6 = make_S8(calib[32])

print("dig_T1 = {}, dig_T2 = {}, dig_T3 = {}".format(dig_T1, dig_T2, dig_T3))
print("dig_P1= {}, dig_P2= {}, dig_P3= {}, dig_P4= {}, dig_P5= {}, dig_P6= {}, dig_P7= {}, dig_P8= {}, dig_P9= {}". format(dig_P1,dig_P2,dig_P3,dig_P4,dig_P5,dig_P6,dig_P7,dig_P8,dig_P9))
print("dig_H1={}, dig_H2={}, dig_H3={}, dig_H4={}, dig_H5={},dig_H6={}".format(dig_H1,dig_H2,dig_H3,dig_H4,dig_H5,dig_H6))

dig_H6 = calib[32]


while True:
    writeRegs([CTRL_HUM_ADDR, 1, CTRL_MEAS_ADDR, 0x25])
    rawPTC = readRegs(PRESS_MSB_ADDR, 8)

    adc_P = (rawPTC[0] << 12 | rawPTC[1] << 4 | rawPTC[2] >> 4)
    adc_T = (rawPTC[3] << 12 | rawPTC[4] << 4 | rawPTC[5] >> 4)
    adc_H = (rawPTC[6] << 8 | rawPTC[7])

    (t_fine, Temp_C) = compensate_T(adc_T)
    Press_Pa = compensate_P(adc_P)
    Hum = compensate_H(adc_H)

    print("Temp_C = {}, Press_Pa={}, Hum={}".format(Temp_C, Press_Pa, Hum))


    print("adc_P={}, adc_T={}, adc_H={}".format(adc_P,adc_T,adc_H))
    time.sleep(2)
     




pi.spi_close(h)
