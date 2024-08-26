import time
import pigpio

class Sensor:

    BME280_ADDR = 0x76
    BME280_ID_ADDR = 0xD0
    CALIB00_ADDR = 0x88
    CALIB26_ADDR = 0xE1
    BME280_RAWDATA_ADDR = 0xF7
    BME280_CTRL_MEAS_ADDR = 0xF4
    BME280_cONFIG_ADDR = 0xF5
    BME280_HUM_ADDR = 0xF2


    def MakeSigned(byte=2):
        def Wrapper(func):                                                 ## Decarotör checks if the short number whetever signed or not, and convert to signed
            def inner(*args, **kwargs):
                ret = func(*args, **kwargs)
                if byte == 1:                                                        ## bir byte işlemde 
                    if ret > 127:
                        ret -= 256
                else:                                                                ## iki byte işlemde ( 16 bit )
                    if ret > 32767:
                        ret -= 65536
                return ret
            return inner
        return Wrapper
    
    def __init__(self,pi = pigpio.pi()):
        self.pi = pi
        self.h = self.pi.i2c_open(1,Sensor.BME280_ADDR)
        self.pi = pigpio.pi()
        self.t_fine = 0.0

        self.LoadCalibration()

    def Read_Byte_Register(self,handle,addr):
        return self.pi.i2c_read_byte_data(handle,addr)
    
    def Read_32Byte_Register(self,handle,addr,count):
        _,b = self.pi.i2c_read_i2c_block_data(handle,addr,count)
        return b
    
    def Write_Byte_Register(self,handle,addr,data):
        self.pi.i2c_write_byte_data(handle,addr,data)

    def LoadCalibration(self):

        callibList = self.Read_32Byte_Register(self.h,self.CALIB00_ADDR,26)

        self.T1 = self._U16(callibList,0)
        self.T2 = self._S16(callibList,2)
        self.T3 = self._S16(callibList,4)

        self.P1 = self._U16(callibList,6)
        self.P2 = self._S16(callibList,8)
        self.P3 = self._S16(callibList,10)
        self.P4= self._S16(callibList,12)
        self.P5 = self._S16(callibList,14)
        self.P6 = self._S16(callibList,16)
        self.P7 = self._S16(callibList,18)
        self.P8 = self._S16(callibList,20)
        self.P9 = self._S16(callibList,22)

        self.H1 = callibList[25]                                                        # U8
        callibList2 = self.Read_32Byte_Register(self.h,Sensor.CALIB26_ADDR,8)           
        self.H2 = self._S16(callibList2,0)
        self.H3 = callibList2[2]

        self.H4 = (callibList2[3] << 4) | (callibList2[4] & 0x0F)
        if self.H4 > 2047:
            self.H4 -= 4096
        self.H5 = (callibList2[5] >> 4) | (callibList2[6] << 4)

        if self.H5 > 2047:
            self.H5 -= 4096
            
        # self.Trim_Byte_Register(callibList2,index=3,target_rangelow=4)
        # self.Trim_Byte_Register(callibList2,index=4,local_rangeup=3)
        # self.H4 = self._S16(callibList2,3)
        # self.Trim_Byte_Register(callibList2,index=5,local_rangelow=4,local_rangeup=7)
        # self.Trim_Byte_Register(callibList2,index=6,target_rangelow=4)
        # self.H5 = self._S16(callibList2,5)


        
        self.H6 = self._S8(callibList2,7)

        print("dig_H1={}, dig_H2={}, dig_H3={}, dig_H4={}, dig_H5={},dig_H6={}".format(self.H1,self.H2,self.H3,self.H4,self.H5,self.H6))

    def _U16(self,calliblist,offset):
        return (calliblist[offset] | calliblist[offset+1] << 8)
    
    @MakeSigned(byte=2)
    def _S16(self,calliblist,offset):
        retval = self._U16(calliblist,offset)
        return retval

    @MakeSigned(byte=1)
    def _S8(self,calliblist,offset):
        retval = calliblist[offset]
        return retval
    
    def Trim_Byte_Register(self,local_List,index,local_rangelow = 0,local_rangeup=7,target_rangelow = 0):
        print("trim öncesi: ",local_List[index])
        mask = (1<<local_rangeup-local_rangelow + 1) - 1
        shifted = (local_List[index] >> local_rangelow) & (mask)
        local_List[index] = (shifted << target_rangelow) & 0xFF 
        print("trim sonrası: ",local_List[index])
    def Read_Raw_Data(self):

        
        self.Write_Byte_Register(self.h, self.BME280_CTRL_MEAS_ADDR,0x25)                       # Pressure and Temperature config ( sampling etc.)
        time.sleep(0.01)
        self.Write_Byte_Register(self.h,self.BME280_HUM_ADDR,0x01)

        # pull adc_raw values 
        d = self.Read_32Byte_Register(self.h,self.BME280_RAWDATA_ADDR,8)

        msb = d[0]
        lsb = d[1]
        xlsb = d[2] >> 4
        adc_p = xlsb | lsb << 4 | msb << 12

        msb = d[3]
        lsb = d[4]
        xlsb = d[5] >> 4
        adc_t = xlsb | lsb << 4 | msb << 12

        msb = d[6]
        lsb = d[7]
        adc_h = msb << 8 | lsb
        
        return adc_t, adc_p, adc_h
    
    def Read_Data(self):

      raw_t, raw_p, raw_h = self.Read_Raw_Data()

      var1 = (raw_t/16384.0 - (self.T1)/1024.0) * float(self.T2)
      var2 = (((raw_t)/131072.0 - (self.T1)/8192.0) *
              ((raw_t)/131072.0 - (self.T1)/8192.0)) * (self.T3)

      self.t_fine = var1 + var2

      t = (var1 + var2) / 5120.0

      var1 = (self.t_fine/2.0) - 64000.0
      var2 = var1 * var1 * self.P6 / 32768.0
      var2 = var2 + (var1 * self.P5 * 2.0)
      var2 = (var2/4.0)+(self.P4 * 65536.0)
      var1 = ((self.P3 * var1 * var1 / 524288.0) + (self.P2 * var1)) / 524288.0
      var1 = (1.0 + var1 / 32768.0)*self.P1
      if var1 != 0.0:
         p = 1048576.0 - raw_p
         p = (p - (var2 / 4096.0)) * 6250.0 / var1
         var1 = self.P9 * p * p / 2147483648.0
         var2 = p * self.P8 / 32768.0
         p = p + (var1 + var2 + self.P7) / 16.0
      else:
         p = 0

      h = self.t_fine - 76800.0

      h = ( (raw_h - ((self.H4) * 64.0 + (self.H5) / 16384.0 * h)) *
            ((self.H2) / 65536.0 * (1.0 + (self.H6) / 67108864.0 * h *
            (1.0 + (self.H3) / 67108864.0 * h))))

      h = h * (1.0 - self.H1 * h / 524288.0)

      if h > 100.0:
         h = 100.0
      elif h < 0.0:
         h = 0.0

      return t, p, h           

    def Close(self):
        if self.h is not None:
            self.pi.i2c_close(self.h)

if __name__ == "__main__":

    import time
    import pigpio
    import BME280_I2C


         
