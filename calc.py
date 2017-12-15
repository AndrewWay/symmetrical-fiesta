#Simple Moving Average (SMA)
#Given some data set, an n-unit moving average period, and a starting point, calculate the SMA

#start, starting index in array of data
#data, array of data
#period, number of elements to use from data array
def SMA(start,period,data):
  sma=-1
  ave=0

  if len(data) >= start :
    if start >= period - 1 :
      for i in range(start-period+1,start+1):
        ave=ave+data[i]
      sma=ave/period
  return sma


#Exponential Moving Average (EMA)
#Given some data set, an n-unit moving average period, and a starting point, calculate the EMA

#start, starting index in array of data
#data, array of data
#period, number of elements to use from data array
def EMA(start,period,data):
  setsize = len(dat)
  ema=-1

  sma=SMA(start,period,data)  
        
  if str(sma) == 'nan':
    return ema
       
  #Calculate the EMA
  multiplier=2/(period+1)
  ema[time[t0]]=sma
  ema_index=t0
    
  for i in range(t0,setsize):
    t=time[i]
    if str(dat[t]) != 'nan':
      old_ema=ema[time[ema_index]]
      current_close=dat[t]
      new_ema=(current_close-old_ema)*multiplier+old_ema
      ema_index=i
      ema[time[ema_index]]=new_ema
  return ema
